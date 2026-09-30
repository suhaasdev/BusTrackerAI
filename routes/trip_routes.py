"""Driver / trip module: assigned bus, start/update/end trip, issues, manifests."""
from datetime import datetime
from flask import Blueprint, request
from utils.database import get_db, serialize
from utils.responses import success, error
from utils.decorators import jwt_required_any, current_user, role_required

trip_bp = Blueprint("trips", __name__)


def _driver_bus(db, driver_id):
    for b in db.buses.find({}):
        if str(b.get("driver_id", "")) == str(driver_id):
            return b
    return None


@trip_bp.get("/api/driver/assigned")
@jwt_required_any
@role_required("driver")
def assigned():
    uid, _, _ = current_user()
    db, _ = get_db()
    bus = _driver_bus(db, uid)
    if not bus:
        # fallback: first bus (demo convenience)
        allb = db.buses.find({})
        bus = allb[0] if allb else None
    if not bus:
        return error("No bus assigned.", "NOT_FOUND", 404)
    b = serialize(bus)
    r = None
    if bus.get("route_id"):
        r = db.routes.find_one({"_id": bus.get("route_id")})
    trip = None
    for t in db.trips.find({}):
        if str(t.get("bus_id")) == str(bus["_id"]) and t.get("status") == "RUNNING":
            trip = t
            break
    if not trip:
        # latest trip for this bus
        cands = [t for t in db.trips.find({}) if str(t.get("bus_id")) == str(bus["_id"])]
        cands.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        trip = cands[0] if cands else None
    return success({"bus": b, "route": serialize(r) if r else None,
                    "trip": serialize(trip) if trip else None})


@trip_bp.post("/api/trips/start")
@jwt_required_any
@role_required("driver")
def start_trip():
    uid, _, _ = current_user()
    data = request.get_json(force=True, silent=True) or {}
    db, _ = get_db()
    bus = _driver_bus(db, uid)
    bus_id = data.get("bus_id") or (str(bus["_id"]) if bus else None)
    if not bus_id:
        return error("bus_id required.", "VALIDATION", 422)
    # close any other running trip for this bus
    for t in db.trips.find({}):
        if str(t.get("bus_id")) == str(bus_id) and t.get("status") == "RUNNING":
            return error("Trip already running for this bus.", "ALREADY_RUNNING", 409)
    target = None
    for b in db.buses.find({}):
        if str(b.get("_id")) == str(bus_id) or str(b.get("bus_number")) == str(bus_id):
            target = b
            break
    if not target:
        return error("Bus not found.", "NOT_FOUND", 404)
    trip = {"bus_id": str(target["_id"]), "bus_number": target.get("bus_number"),
            "driver_id": str(uid), "route_id": str(target.get("route_id", "")),
            "status": "RUNNING", "start_time": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()}
    tid = db.trips.insert_one(trip).inserted_id
    db.buses.update_one({"_id": target["_id"]}, {"$set": {"status": "DEPARTED"}})
    trip["_id"] = tid
    return success({"trip": serialize(trip)}, "Trip started.", 201)


@trip_bp.post("/api/trips/location")
@jwt_required_any
@role_required("driver")
def update_location():
    uid, _, _ = current_user()
    data = request.get_json(force=True, silent=True) or {}
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return error("Valid latitude/longitude required.", "VALIDATION", 422)
    speed = float(data.get("speed", 40) or 40)
    bus_id = data.get("bus_id")
    db, _ = get_db()
    bus = None
    if bus_id:
        for b in db.buses.find({}):
            if str(b.get("_id")) == str(bus_id) or str(b.get("bus_number")) == str(bus_id):
                bus = b
                break
    else:
        bus = _driver_bus(db, uid)
    if not bus:
        return error("Bus not found.", "NOT_FOUND", 404)
    now = datetime.utcnow().isoformat()
    loc = {"bus_id": str(bus["_id"]), "bus_number": bus.get("bus_number"),
           "latitude": lat, "longitude": lon, "speed": speed,
           "current_location": data.get("current_location", "en route"),
           "status": data.get("status", "ON_TIME"),
           "updated_at": now, "timestamp": now}
    # upsert into tracking + append to locations history
    existing = None
    for t in db.tracking.find({}):
        if str(t.get("bus_id")) == str(bus["_id"]):
            existing = t
            break
    if existing:
        db.tracking.update_one({"_id": existing["_id"]}, {"$set": loc})
    else:
        db.tracking.insert_one(dict(loc, eta_minutes=30))
    try:
        db.locations.insert_one(dict(loc))
    except Exception:
        pass
    return success({"location": loc}, "Location updated.")


@trip_bp.post("/api/trips/end")
@jwt_required_any
@role_required("driver")
def end_trip():
    uid, _, _ = current_user()
    data = request.get_json(force=True, silent=True) or {}
    db, _ = get_db()
    trip = None
    if data.get("trip_id"):
        for t in db.trips.find({}):
            if str(t.get("_id")) == str(data.get("trip_id")):
                trip = t
                break
    else:
        for t in db.trips.find({}):
            if str(t.get("driver_id")) == str(uid) and t.get("status") == "RUNNING":
                trip = t
                break
    if not trip:
        return error("No running trip found.", "NOT_FOUND", 404)
    db.trips.update_one({"_id": trip["_id"]}, {"$set": {"status": "COMPLETED",
                                                        "end_time": datetime.utcnow().isoformat()}})
    try:
        db.buses.update_one({"_id": trip.get("bus_id")}, {"$set": {"status": "COMPLETED"}})
    except Exception:
        # memory store ids are strings — try scan
        for b in db.buses.find({}):
            if str(b.get("_id")) == str(trip.get("bus_id")):
                db.buses.update_one({"_id": b["_id"]}, {"$set": {"status": "COMPLETED"}})
                break
    trip["status"] = "COMPLETED"
    return success({"trip": serialize(trip)}, "Trip completed.")


@trip_bp.post("/api/trips/report")
@jwt_required_any
@role_required("driver")
def report_issue():
    uid, _, _ = current_user()
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or data.get("issue") or "").strip()
    if not text:
        return error("Issue text required.", "VALIDATION", 422)
    db, _ = get_db()
    doc = {"driver_id": str(uid), "bus_id": data.get("bus_id", ""),
           "text": text, "created_at": datetime.utcnow().isoformat()}
    db.issues.insert_one(doc)
    return success({"report": serialize(doc)}, "Issue reported.", 201)


@trip_bp.get("/api/driver/manifest")
@jwt_required_any
@role_required("driver")
def manifest():
    """Passenger booking info for driver's bus (privacy: names + seats only)."""
    uid, _, _ = current_user()
    db, _ = get_db()
    bus = _driver_bus(db, uid)
    bus_id = (request.args.get("bus_id") or (str(bus["_id"]) if bus else "") or "")
    date = (request.args.get("date") or "").strip()
    out = []
    for bk in db.bookings.find({}):
        if bus_id and str(bk.get("bus_id")) != str(bus_id):
            # also match by bus_number
            if str(bk.get("bus_number", "")) != str(bus_id):
                continue
        if date and bk.get("travel_date") != date:
            continue
        if bk.get("status") != "CONFIRMED":
            continue
        out.append({"booking_id": bk.get("booking_id"), "seats": bk.get("seats"),
                    "passengers": [{"name": p.get("name"), "age": p.get("age")}
                                   for p in bk.get("passengers", [])],
                    "travel_date": bk.get("travel_date")})
    return success({"manifest": out, "count": len(out)})
