"""Multi-factor bus recommendation (prototype scoring).

score = fare_score + duration_score + availability_score + time_score
Higher is better. Clearly a heuristic until an ML model replaces it.
"""
from datetime import datetime


def _to_minutes(t):
    try:
        h, m = str(t).split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return 8 * 60


def score_bus(bus, prefs=None):
    prefs = prefs or {}
    fare = float(bus.get("fare", 100))
    dep = _to_minutes(bus.get("departure_time", "08:00"))
    arr = _to_minutes(bus.get("arrival_time", "10:00"))
    duration = max(30, arr - dep if arr > dep else (24 * 60 - dep + arr))
    booked = bus.get("booked_seats") or []
    total = int(bus.get("total_seats", 40))
    avail = max(0, total - len(booked))

    fare_score = max(0, 40 - fare / 5)            # cheaper -> higher
    duration_score = max(0, 30 - duration / 10)   # shorter -> higher
    availability_score = min(20, avail / max(1, total) * 20)
    time_score = 10
    pref_time = (prefs.get("preferred_time") or "").lower()
    if pref_time == "morning" and 5 * 60 <= dep < 12 * 60:
        time_score = 10
    elif pref_time == "afternoon" and 12 * 60 <= dep < 17 * 60:
        time_score = 10
    elif pref_time == "evening" and 17 * 60 <= dep < 21 * 60:
        time_score = 10
    elif pref_time == "night" and (dep >= 21 * 60 or dep < 5 * 60):
        time_score = 10
    elif pref_time:
        time_score = 4
    status_bonus = 5 if str(bus.get("status", "ON_TIME")).upper() == "ON_TIME" else -5
    total_score = round(fare_score + duration_score + availability_score + time_score + status_bonus, 1)
    return total_score


def recommend(buses, prefs=None, top_n=3):
    prefs = prefs or {}
    scored = [(score_bus(b, prefs), b) for b in buses]
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for score, b in scored[:top_n]:
        c = dict(b)
        c["_ai_score"] = score
        out.append(c)
    return out
