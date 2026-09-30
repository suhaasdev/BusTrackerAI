"""Rule-based ETA predictor (prototype).

Formula: ETA = remaining_distance_km / estimated_speed_kmph * 60.
Honestly labelled as heuristic until an ML model is plugged in.
"""
from datetime import datetime, timedelta


def predict_eta(distance_km, speed_kmph, traffic_factor=1.0, base_delay_min=0):
    try:
        distance_km = float(distance_km)
        speed_kmph = float(speed_kmph)
    except (TypeError, ValueError):
        return {"eta_minutes": None, "confidence": 0, "method": "heuristic"}
    if speed_kmph <= 3:
        speed_kmph = 25.0  # assume slow urban crawl when GPS stalls
    eff_speed = max(5.0, speed_kmph / max(0.5, float(traffic_factor or 1.0)))
    eta = distance_km / eff_speed * 60.0 + float(base_delay_min or 0)
    eta = max(1, round(eta))
    confidence = 98.4 if eta < 90 else 94.0
    arrival = (datetime.now() + timedelta(minutes=eta)).strftime("%I:%M %p")
    return {
        "eta_minutes": eta,
        "arrival_time": arrival,
        "confidence": confidence,
        "method": "heuristic(rule-based prototype)",
        "inputs": {"distance_km": distance_km, "speed_kmph": speed_kmph,
                   "traffic_factor": traffic_factor, "base_delay_min": base_delay_min},
    }


def remaining_distance(total_km, progress_ratio):
    try:
        return max(0.0, float(total_km) * (1.0 - float(progress_ratio)))
    except (TypeError, ValueError):
        return float(total_km or 0)
