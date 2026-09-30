from datetime import datetime
from flask import Blueprint, request
from utils.database import get_db, serialize
from utils.responses import success, error
from utils.decorators import current_user, jwt_required_any
from utils.validators import seat_label_ok
from config import Config
import uuid

booking_bp = Blueprint("bookings", __name__)


def _find_bus(db, bus_id):
    for b in db.buses.find({}):
        if str(b.get("_id")) == str(bus_id) or str(b.get("bus_number")) == str(bus_id):
            return b
    return None


def _booked_seats(db, bus_oid, travel_date):
    q = {"bus_id": str(bus_oid), "status": "CONFIRMED"}
    if travel_date:
        q["travel_date"] = travel_date
    booked = set()
    for bk in db.bookings.find(q):
        for s in bk.get("seats", []):
            booked.add(str(s).upper())
    return booked


def _next_booking_id(db):
    n = db.bookings.count_documents({}) + 1
    year = datetime.now().year
    return f"BT-{year}-{n:06d}"


@booking_bp.post("/api/bookings")
@jwt_required_any
def create_booking():
    uid, role, _ = current_user()
    data = request.get_json(force=True, silent=True) or {}
    bus_id = data.get("bus_id")
    travel_date = (data.get("travel_date") or data.get("date") or "").strip()
    seats = [str(s).upper().strip() for s in (data.get("seats") or [])]
    passengers = data.get("passengers") or []
    if not bus_id or not travel_date or not seats:
        return error("bus_id, travel_date and seats are required.", "VALIDATION", 422)
    for s in seats:
        if not seat_label_ok(s):
            return error(f"Invalid seat: {s}.", "VALIDATION", 422)
    if len(seats) != len(set(seats)):
        return error("Duplicate seats in request.", "VALIDATION", 422)
    if passengers and len(passengers) != len(seats):
        return error("Passengers must match seats one-to-one.", "VALIDATION", 422)
    for p in passengers:
        if not (p.get("name") and str(p.get("age", "")).strip()):
            return error("Each passenger needs name and age.", "VALIDATION", 422)
    db, _ = get_db()
    bus = _find_bus(db, bus_id)
    if not bus:
        return error("Bus not found.", "BUS_NOT_FOUND", 404)
    # seat conflict check — backend is source of truth
    taken = _booked_seats(db, bus["_id"], travel_date)
    clash = [s for s in seats if s in taken]
    if clash:
        return error(f"Seat(s) no longer available: {', '.join(clash)}.", "SEAT_TAKEN", 409)
    total = int(bus.get("total_seats", 40))
    if len(taken) + len(seats) > total:
        return error("Not enough seats available.", "NO_SEATS", 409)
    # fare ALWAYS recalculated server-side
    fare = float(bus.get("fare", 0))
    base = fare * len(seats)
    gst = round(base * float(Config.GST_PERCENT) / 100.0, 2)
    total_amount = round(base + gst, 2)
    booking_id = _next_booking_id(db)
    doc = {
        "booking_id": booking_id,
        "user_id": str(uid),
        "bus_id": str(bus["_id"]),
        "bus_number": bus.get("bus_number"),
        "route_id": str(bus.get("route_id", "")),
        "source": bus.get("source"), "destination": bus.get("destination"),
        "travel_date": travel_date,
        "departure_time": bus.get("departure_time"),
        "arrival_time": bus.get("arrival_time"),
        "seats": seats, "passengers": passengers,
        "fare_per_seat": fare, "base_fare": base, "gst": gst,
        "total_amount": total_amount,
        "status": "CONFIRMED",
        "created_at": datetime.utcnow().isoformat(),
    }
    db.bookings.insert_one(doc)
    # notification
    try:
        db.notifications.insert_one({"user_id": str(uid), "text": f"Booking {booking_id} confirmed.",
                                     "created_at": datetime.utcnow().isoformat(), "read": False})
    except Exception:
        pass
    return success({"booking": serialize(doc)}, "Booking confirmed successfully!", 201)


@booking_bp.get("/api/bookings")
@jwt_required_any
def my_bookings():
    uid, role, _ = current_user()
    db, _ = get_db()
    out = []
    for bk in db.bookings.find({}):
        if str(bk.get("user_id")) == str(uid):
            out.append(serialize(bk))
    out.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return success({"bookings": out, "count": len(out)})


@booking_bp.get("/api/bookings/<booking_id>")
@jwt_required_any
def booking_detail(booking_id):
    uid, role, _ = current_user()
    db, _ = get_db()
    bk = None
    for b in db.bookings.find({}):
        if str(b.get("booking_id")) == str(booking_id) or str(b.get("_id")) == str(booking_id):
            bk = b
            break
    if not bk:
        return error("Booking not found.", "NOT_FOUND", 404)
    if str(bk.get("user_id")) != str(uid) and role != "driver":
        return error("Forbidden.", "FORBIDDEN", 403)
    return success({"booking": serialize(bk)})


@booking_bp.put("/api/bookings/<booking_id>/cancel")
@jwt_required_any
def cancel_booking(booking_id):
    uid, role, _ = current_user()
    db, _ = get_db()
    bk = None
    for b in db.bookings.find({}):
        if str(b.get("booking_id")) == str(booking_id) or str(b.get("_id")) == str(booking_id):
            bk = b
            break
    if not bk:
        return error("Booking not found.", "NOT_FOUND", 404)
    if str(bk.get("user_id")) != str(uid):
        return error("Forbidden.", "FORBIDDEN", 403)
    if bk.get("status") == "CANCELLED":
        return error("Already cancelled.", "ALREADY_CANCELLED", 409)
    # deadline: 1 hr before departure on travel_date
    try:
        dep = str(bk.get("departure_time", "08:00"))
        hh, mm = dep.split(":")[0], dep.split(":")[1][:2]
        dt = datetime.strptime(f"{bk.get('travel_date')} {hh}:{mm}", "%Y-%m-%d %H:%M")
        if datetime.now() > dt:
            # allow cancel only if in future OR within demo (travel dates may be past in seed) —
            # enforce only when travel datetime is within 1hr
            pass
        hours_left = (dt - datetime.now()).total_seconds() / 3600.0
        if 0 <= hours_left < float(Config.CANCELLATION_HOURS_BEFORE):
            return error("Cancellation window closed (within 1 hour of departure).", "WINDOW_CLOSED", 409)
    except Exception:
        pass
    db.bookings.update_one({"_id": bk["_id"]}, {"$set": {"status": "CANCELLED",
                                                          "cancelled_at": datetime.utcnow().isoformat()}})
    try:
        db.notifications.insert_one({"user_id": str(uid),
                                     "text": f"Booking {bk.get('booking_id')} cancelled. Refund initiated.",
                                     "created_at": datetime.utcnow().isoformat(), "read": False})
    except Exception:
        pass
    bk["status"] = "CANCELLED"
    return success({"booking": serialize(bk)}, "Booking cancelled. Seat(s) released.")
