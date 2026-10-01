"""Admin APIs: stats, users, buses CRUD, bookings, tracking, analytics.
Every endpoint requires role=admin."""
from datetime import datetime
from flask import Blueprint, request
from utils.database import get_db, serialize
from utils.responses import success, error
from utils.decorators import jwt_required_any, current_user, role_required

admin_bp = Blueprint("admin", __name__)
guard = [jwt_required_any, role_required("admin")]


def _all(col):
    db, _ = get_db()
    return db, [serialize(d) for d in db[col].find({})]


def _find(db, col, key):
    for d in db[col].find({}):
        if str(d.get("_id")) == str(key):
            return d
    return None


@admin_bp.get("/api/admin/stats")
@jwt_required_any
@role_required("admin")
def stats():
    db, _ = get_db()
    users = [serialize(u) for u in db.users.find({})]
    buses = [serialize(b) for b in db.buses.find({})]
    bookings = [serialize(x) for x in db.bookings.find({})]
    today = datetime.now().strftime("%Y-%m-%d")
    confirmed = [b for b in bookings if b.get("status") == "CONFIRMED"]
    revenue = round(sum(float(b.get("total_amount", 0) or 0) for b in confirmed), 2)
    ontime = sum(1 for b in buses if str(b.get("status", "")).upper() == "ON_TIME")
    return success({
        "total_users": len(users), "total_buses": len(buses),
        "total_bookings": len(bookings),
        "today_bookings": sum(1 for b in bookings if str(b.get("travel_date", "")) == today),
        "active_buses": sum(1 for b in buses if str(b.get("status", "")).upper() in ("ON_TIME", "DEPARTED", "ARRIVING")),
        "revenue": revenue,
        "on_time_rate": round(ontime / len(buses) * 100, 1) if buses else 0,
    })


@admin_bp.get("/api/admin/users")
@jwt_required_any
@role_required("admin")
def list_users():
    db, users = _all("users")
    for u in users:
        u.pop("password_hash", None)
    users.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return success({"users": users, "count": len(users)})


@admin_bp.put("/api/admin/users/<uid>")
@jwt_required_any
@role_required("admin")
def toggle_user(uid):
    me, _, _ = current_user()
    db, _ = get_db()
    u = _find(db, "users", uid)
    if not u:
        return error("User not found.", "NOT_FOUND", 404)
    if str(u["_id"]) == str(me):
        return error("You cannot disable your own admin account.", "VALIDATION", 422)
    data = request.get_json(force=True, silent=True) or {}
    status = (data.get("status") or "").lower()
    if status not in ("active", "disabled"):
        status = "disabled" if u.get("status") == "active" else "active"
    db.users.update_one({"_id": u["_id"]}, {"$set": {"status": status}})
    return success({"user_id": str(u["_id"]), "status": status}, f"User {status}.")


@admin_bp.get("/api/admin/bookings")
@jwt_required_any
@role_required("admin")
def all_bookings():
    db, bookings = _all("bookings")
    bookings.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return success({"bookings": bookings, "count": len(bookings)})


@admin_bp.post("/api/admin/buses")
@jwt_required_any
@role_required("admin")
def add_bus():
    data = request.get_json(force=True, silent=True) or {}
    need = ["bus_number", "operator", "source", "destination", "departure_time", "arrival_time", "fare", "total_seats"]
    missing = [f for f in need if data.get(f) in (None, "")]
    if missing:
        return error(f"Missing fields: {', '.join(missing)}.", "VALIDATION", 422)
    db, _ = get_db()
    if db.buses.find_one({"bus_number": str(data["bus_number"]).strip()}):
        return error("Bus number already exists.", "DUPLICATE", 409)
    # attach matching route if any
    route_id = data.get("route_id", "")
    if not route_id:
        for r in db.routes.find({}):
            if (str(r.get("source", "")).lower() == str(data["source"]).lower() and
                    str(r.get("destination", "")).lower() == str(data["destination"]).lower()):
                route_id = str(r["_id"])
                break
    try:
        fare = float(data["fare"]); seats = int(data["total_seats"])
    except (TypeError, ValueError):
        return error("fare must be a number, total_seats an integer.", "VALIDATION", 422)
    bus = {"bus_number": str(data["bus_number"]).strip(), "operator": str(data["operator"]).strip(),
           "bus_name": str(data.get("bus_name", "")).strip(), "bus_type": str(data.get("bus_type", "Express")).strip(),
           "source": str(data["source"]).strip(), "destination": str(data["destination"]).strip(),
           "route_id": route_id, "departure_time": str(data["departure_time"]).strip(),
           "arrival_time": str(data["arrival_time"]).strip(), "fare": fare, "total_seats": seats,
           "status": str(data.get("status", "ON_TIME")).upper(),
           "created_at": datetime.utcnow().isoformat()}
    nid = db.buses.insert_one(bus).inserted_id
    bus["_id"] = nid
    return success({"bus": serialize(bus)}, "Bus added.", 201)


@admin_bp.put("/api/admin/buses/<bid>")
@jwt_required_any
@role_required("admin")
def edit_bus(bid):
    data = request.get_json(force=True, silent=True) or {}
    db, _ = get_db()
    b = _find(db, "buses", bid)
    if not b:
        return error("Bus not found.", "NOT_FOUND", 404)
    patch = {}
    for f in ("operator", "bus_name", "bus_type", "source", "destination",
              "route_id", "departure_time", "arrival_time", "status", "driver_id"):
        if data.get(f) not in (None, ""):
            patch[f] = str(data[f]).strip().upper() if f == "status" else data[f]
    if data.get("fare") not in (None, ""):
        try:
            patch["fare"] = float(data["fare"])
        except (TypeError, ValueError):
            return error("fare must be a number.", "VALIDATION", 422)
    if data.get("total_seats") not in (None, ""):
        try:
            patch["total_seats"] = int(data["total_seats"])
        except (TypeError, ValueError):
            return error("total_seats must be an integer.", "VALIDATION", 422)
    if patch:
        db.buses.update_one({"_id": b["_id"]}, {"$set": patch})
    nb = _find(db, "buses", bid)
    return success({"bus": serialize(nb)}, "Bus updated.")


@admin_bp.delete("/api/admin/buses/<bid>")
@jwt_required_any
@role_required("admin")
def delete_bus(bid):
    db, _ = get_db()
    b = _find(db, "buses", bid)
    if not b:
        return error("Bus not found.", "NOT_FOUND", 404)
    has_active = any(True for bk in db.bookings.find(
        {"bus_id": str(b["_id"]), "status": "CONFIRMED"}))
    if has_active:
        return error("Cannot delete: bus has confirmed bookings.", "HAS_BOOKINGS", 409)
    db.buses.delete_one({"_id": b["_id"]})
    return success({}, "Bus deleted.")


@admin_bp.put("/api/admin/tracking/<bus_id>")
@jwt_required_any
@role_required("admin")
def update_tracking(bus_id):
    data = request.get_json(force=True, silent=True) or {}
    db, _ = get_db()
    bus = None
    for b in db.buses.find({}):
        if str(b.get("_id")) == str(bus_id) or str(b.get("bus_number")) == str(bus_id):
            bus = b
            break
    if not bus:
        return error("Bus not found.", "NOT_FOUND", 404)
    try:
        lat = float(data.get("latitude", 18.12)); lon = float(data.get("longitude", 83.40))
    except (TypeError, ValueError):
        return error("latitude/longitude must be numbers.", "VALIDATION", 422)
    now = datetime.utcnow().isoformat()
    loc = {"bus_id": str(bus["_id"]), "bus_number": bus.get("bus_number"),
           "latitude": lat, "longitude": lon, "speed": float(data.get("speed", 40) or 40),
           "current_location": data.get("current_location", "depot"),
           "status": str(data.get("status", bus.get("status", "ON_TIME"))).upper(),
           "eta_minutes": data.get("eta_minutes", 30),
           "updated_at": now, "timestamp": now, "simulated": True}
    existing = next((t for t in db.tracking.find({})
                     if str(t.get("bus_id")) == str(bus["_id"])), None)
    if existing:
        db.tracking.update_one({"_id": existing["_id"]}, {"$set": loc})
    else:
        db.tracking.insert_one(dict(loc))
    try:
        db.locations.insert_one(dict(loc))
    except Exception:
        pass
    if data.get("status"):
        db.buses.update_one({"_id": bus["_id"]}, {"$set": {"status": loc["status"]}})
    return success({"tracking": loc}, "Tracking updated.")


@admin_bp.get("/api/admin/analytics")
@jwt_required_any
@role_required("admin")
def analytics():
    db, _ = get_db()
    bookings = [serialize(b) for b in db.bookings.find({})]
    per_day, rev_day, routes, per_bus = {}, {}, {}, {}
    for b in bookings:
        d = str(b.get("travel_date", "unknown"))
        per_day[d] = per_day.get(d, 0) + 1
        if b.get("status") == "CONFIRMED":
            rev_day[d] = round(rev_day.get(d, 0) + float(b.get("total_amount", 0) or 0), 2)
        rk = f"{b.get('source', '?')} → {b.get('destination', '?')}"
        routes[rk] = routes.get(rk, 0) + 1
        per_bus[b.get("bus_number", "?")] = per_bus.get(b.get("bus_number", "?"), 0) + 1
    days = sorted(per_day)
    return success({
        "bookings_per_day": {"labels": days, "values": [per_day[d] for d in days]},
        "revenue_per_day": {"labels": sorted(rev_day), "values": [rev_day[d] for d in sorted(rev_day)]},
        "popular_routes": sorted(routes.items(), key=lambda x: x[1], reverse=True)[:6],
        "bus_usage": sorted(per_bus.items(), key=lambda x: x[1], reverse=True)[:6],
    })
