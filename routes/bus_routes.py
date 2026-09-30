from flask import Blueprint, request
from utils.database import get_db, serialize
from utils.responses import success, error
from utils.decorators import current_user, role_required

bus_bp = Blueprint("buses", __name__)
route_bp = Blueprint("busroutes", __name__)


def _avail(bus, travel_date=None):
    db, _ = get_db()
    q = {"bus_id": str(bus["_id"]), "status": "CONFIRMED"}
    if travel_date:
        q["travel_date"] = travel_date
    booked = []
    for bk in db.bookings.find(q):
        booked.extend(bk.get("seats", []))
    return booked


@bus_bp.get("/api/buses")
def list_buses():
    source = (request.args.get("source") or "").strip()
    destination = (request.args.get("destination") or "").strip()
    travel_date = (request.args.get("date") or request.args.get("travel_date") or "").strip()
    bus_type = (request.args.get("bus_type") or "").strip()
    sort = (request.args.get("sort") or "").strip()
    db, _ = get_db()
    buses = [serialize(b) for b in db.buses.find({})]

    def match(b):
        if source and source.lower() not in str(b.get("source", "")).lower():
            return False
        if destination and destination.lower() not in str(b.get("destination", "")).lower():
            return False
        if bus_type and bus_type.lower() != "all" and bus_type.lower() not in str(b.get("bus_type", "")).lower():
            return False
        return True

    out = []
    for b in buses:
        if not match(b):
            continue
        booked = _avail({"_id": b["_id"], "status": b.get("status")}, travel_date or None) if False else None
        # compute booked seats for date (or all confirmed if no date)
        q = {"bus_id": str(b["_id"]), "status": "CONFIRMED"}
        if travel_date:
            q["travel_date"] = travel_date
        booked = []
        for bk in db.bookings.find(q):
            booked.extend([s.upper() for s in bk.get("seats", [])])
        b["booked_seats"] = booked
        b["available_count"] = int(b.get("total_seats", 40)) - len(booked)
        # attach route stops
        r = db.routes.find_one({"_id": b.get("route_id")}) if b.get("route_id") else None
        if not r:
            # fallback match by source/destination
            for rr in db.routes.find({}):
                if (str(rr.get("source", "")).lower() in str(b.get("source", "")).lower() or
                        str(b.get("source", "")).lower() in str(rr.get("source", "")).lower()):
                    r = rr
                    break
        b["route"] = serialize(r) if r else None
        # stringify ids
        b["id"] = str(b["_id"])
        out.append(b)

    if sort == "price_asc":
        out.sort(key=lambda x: float(x.get("fare", 0)))
    elif sort == "price_desc":
        out.sort(key=lambda x: float(x.get("fare", 0)), reverse=True)
    elif sort == "departure":
        out.sort(key=lambda x: str(x.get("departure_time", "")))
    return success({"buses": out, "count": len(out)})


@bus_bp.get("/api/buses/<bus_id>")
def bus_detail(bus_id):
    db, _ = get_db()
    bus = None
    for b in db.buses.find({}):
        if str(b.get("_id")) == str(bus_id) or str(b.get("bus_number")) == str(bus_id):
            bus = b
            break
    if not bus:
        return error("Bus not found.", "BUS_NOT_FOUND", 404)
    b = serialize(bus)
    travel_date = (request.args.get("date") or "").strip()
    q = {"bus_id": str(bus["_id"]), "status": "CONFIRMED"}
    if travel_date:
        q["travel_date"] = travel_date
    booked = []
    for bk in db.bookings.find(q):
        booked.extend([s.upper() for s in bk.get("seats", [])])
    b["booked_seats"] = booked
    b["available_count"] = int(b.get("total_seats", 40)) - len(booked)
    b["id"] = str(bus["_id"])
    r = db.routes.find_one({"_id": bus.get("route_id")}) if bus.get("route_id") else None
    b["route"] = serialize(r) if r else None
    t = db.tracking.find_one({"bus_id": str(bus["_id"])}) if hasattr(db, "tracking") else None
    # tracking collection name is 'tracking'/'locations' — check both
    if not t:
        try:
            t = db.locations.find_one({"bus_id": str(bus["_id"])})
        except Exception:
            t = None
    b["tracking"] = serialize(t) if t else None
    return success({"bus": b})


@route_bp.get("/api/routes")
def list_routes():
    db, _ = get_db()
    routes = [serialize(r) for r in db.routes.find({})]
    for r in routes:
        r["id"] = str(r.get("_id"))
    return success({"routes": routes})


@route_bp.get("/api/routes/<route_id>")
def route_detail(route_id):
    db, _ = get_db()
    for r in db.routes.find({}):
        if str(r.get("_id")) == str(route_id):
            d = serialize(r)
            d["id"] = str(r.get("_id"))
            return success({"route": d})
    return error("Route not found.", "NOT_FOUND", 404)
