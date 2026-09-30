"""Delay classifier (prototype, rule-based)."""


def predict_delay(speed_kmph, scheduled_speed=42.0, congestion_index=0.1, hour=None):
    try:
        s = float(speed_kmph or 0)
    except (TypeError, ValueError):
        s = 0
    from datetime import datetime
    h = hour if hour is not None else datetime.now().hour
    score = 0
    if s < 15:
        score += 3
    elif s < 25:
        score += 2
    elif s < 35:
        score += 1
    if (congestion_index or 0) > 0.6:
        score += 2
    elif (congestion_index or 0) > 0.3:
        score += 1
    if h in (8, 9, 18, 19):
        score += 1  # peak hours
    if score >= 5:
        return {"level": "High delay", "delay_minutes": 20, "css": "danger"}
    if score >= 3:
        return {"level": "Moderate delay", "delay_minutes": 12, "css": "warning"}
    if score >= 2:
        return {"level": "Slight delay", "delay_minutes": 6, "css": "warning"}
    return {"level": "On-time", "delay_minutes": 0, "css": "success"}
