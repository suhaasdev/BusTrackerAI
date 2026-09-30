from flask import Blueprint, request
from utils.database import get_db, serialize
from utils.responses import success, error
from ai.eta_predictor import predict_eta, remaining_distance
from ai.delay_predictor import predict_delay

tracking_bp = Blueprint("tracking", __name__)


def _find_bus(db, bus_id):
    for b in db.buses.find({}):
        if str(b.get("_id")) == str(bus_id) or str(b.get("bus_number")) == str(bus_id):
            return b
    return None


@tracking_bp.get("/api/tracking/<bus_id>")
def get_tracking(bus_id):
    db, _ = get_db()
    bus = _find_bus(db, bus_id)
    if not bus:
        return error("Bus not found.", "BUS_NOT_FOUND", 404)
    t = None
    for doc in db.tracking.find({}):
        if str(doc.get("bus_id")) == str(bus["_id"]) or \
           str(doc.get("bus_number", "")) == str(bus.get("bus_number")):
            t = doc
            break
    # route distance for ETA fallback
    r = db.routes.find_one({"_id": bus.get("route_id")}) if bus.get("route_id") else None
    total_km = (r or {}).get("distance_km", 60)
    if not t:
        # simulated tracking (clearly demo data)
        t = {"bus_id": str(bus["_id"]), "bus_number": bus.get("bus_number"),
             "latitude": 18.1219, "longitude": 83.4024,
             "current_location": "Vizianagaram Depot (simulated)",
             "speed": 0, "status": bus.get("status", "ON_TIME"),
             "eta_minutes": None, "simulated": True}
        eta = predict_eta(total_km, 38)
        t["eta_minutes"] = eta["eta_minutes"]
        t["eta_detail"] = eta
        t["delay"] = predict_delay(0)
        return success({"tracking": t, "bus": serialize(bus), "simulated": True})
    t = serialize(t)
    # compute remaining distance heuristically from progress if present
    progress = t.get("progress_ratio", 0.35)
    rem = remaining_distance(total_km, progress if isinstance(progress, (int, float)) else 0.35)
    eta = predict_eta(rem if rem else total_km * 0.5, t.get("speed", 40))
    t["eta_minutes"] = t.get("eta_minutes") or eta["eta_minutes"]
    t["eta_detail"] = eta
    t["delay"] = predict_delay(t.get("speed", 40))
    t["distance_km"] = total_km
    return success({"tracking": t, "bus": serialize(bus), "simulated": bool(t.get("simulated", False))})
