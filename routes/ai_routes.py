from flask import Blueprint, request
from utils.database import get_db, serialize
from utils.responses import success, error
from ai.travel_assistant import answer
from ai.recommendation_engine import recommend
from ai.eta_predictor import predict_eta

ai_bp = Blueprint("ai", __name__)


def _bus_ctx(db, source="", destination=""):
    buses = []
    for b in db.buses.find({}):
        if source and source.lower() not in str(b.get("source", "")).lower():
            continue
        if destination and destination.lower() not in str(b.get("destination", "")).lower():
            continue
        d = serialize(b)
        # attach booked seats
        booked = []
        for bk in db.bookings.find({"bus_id": str(b["_id"]), "status": "CONFIRMED"}):
            booked.extend([s.upper() for s in bk.get("seats", [])])
        d["booked_seats"] = booked
        buses.append(d)
    tracking = {}
    for t in db.tracking.find({}):
        tracking[t.get("bus_number", "")] = serialize(t)
    return {"buses": buses, "tracking": tracking}


@ai_bp.post("/api/ai/chat")
def chat():
    data = request.get_json(force=True, silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return error("Message is required.", "VALIDATION", 422)
    src = (data.get("source") or "").strip()
    dst = (data.get("destination") or "").strip()
    # auto-extract Vizianagaram/Visakhapatnam style corridor from message
    import re
    m = re.search(r"from\s+([A-Za-z]+)\s+to\s+([A-Za-z]+)", msg, re.I)
    if m and not src:
        src, dst = m.group(1), m.group(2)
    db, _ = get_db()
    ctx = _bus_ctx(db, src, dst)
    if not ctx["buses"] and (src or dst):
        ctx = _bus_ctx(db)  # fall back to all buses rather than hallucinating
    reply = answer(msg, ctx)
    try:
        db.ai_conversations.insert_one({"message": msg, "response": reply})
    except Exception:
        pass
    return success({"response": reply, "intent_engine": "rule-based prototype"})


@ai_bp.post("/api/ai/recommend")
def recommend_api():
    data = request.get_json(force=True, silent=True) or {}
    db, _ = get_db()
    ctx = _bus_ctx(db, data.get("source", ""), data.get("destination", ""))
    recs = recommend(ctx["buses"], {"preferred_time": data.get("preferred_time", ""),
                                    "budget": data.get("budget")}, top_n=3)
    return success({"recommendations": recs,
                    "note": "Prototype heuristic scoring (fare + duration + availability + time)."})


@ai_bp.get("/api/ai/eta/<bus_id>")
def eta_api(bus_id):
    db, _ = get_db()
    bus = None
    for b in db.buses.find({}):
        if str(b.get("_id")) == str(bus_id) or str(b.get("bus_number")) == str(bus_id):
            bus = b
            break
    if not bus:
        return error("Bus not found.", "NOT_FOUND", 404)
    t = None
    for d in db.tracking.find({}):
        if str(d.get("bus_id")) == str(bus["_id"]):
            t = d
            break
    speed = (t or {}).get("speed", 40)
    r = db.routes.find_one({"_id": bus.get("route_id")}) if bus.get("route_id") else None
    dist = (r or {}).get("distance_km", 60)
    res = predict_eta(float(dist) * 0.5, float(speed))
    return success({"eta": res, "bus_number": bus.get("bus_number")})
