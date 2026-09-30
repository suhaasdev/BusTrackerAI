"""Intent-based travel assistant grounded in real DB data.

Never fabricates buses: every recommendation / fare / ETA answer is
computed from actual MongoDB (or in-memory) documents passed in.
"""
import re
from datetime import datetime


def detect_intent(msg):
    m = (msg or "").lower()
    if re.search(r"where\s+is|location|track|live|gps|reached|arriv.*(where|now)", m):
        return "track_bus"
    if "cheapest" in m or "lowest fare" in m or "low price" in m:
        return "cheapest"
    if "earliest" in m:
        return "earliest"
    if re.search(r"before\s+\d|arriv.*before|reach.*before|morning", m):
        return "before_time"
    if "seat" in m and ("most" in m or "availab" in m or "empty" in m):
        return "most_seats"
    if "eta" in m or "how long" in m or "when.*(reach|arrive)" in m or "estimated" in m:
        return "eta"
    if "cancel" in m or "refund" in m:
        return "cancel_policy"
    if re.search(r"bus.*(from|to)|recommend|suggest|which bus|need.*(travel|reach|go)", m):
        return "search"
    if "hello" in m or "hi" == m.strip() or "hey" in m:
        return "greet"
    return "general"


def _fmt_bus(b):
    return (f"{b.get('bus_number')} ({b.get('operator','')} - {b.get('bus_type','')}) "
            f"departs {b.get('departure_time')} arrives {b.get('arrival_time')}, "
            f"fare Rs.{b.get('fare')}")


def answer(message, ctx):
    """ctx: {buses:[...], tracking:{bus_number: {...}}, routes:[...]}"""
    buses = ctx.get("buses", []) or []
    tracking = ctx.get("tracking", {}) or {}
    intent = detect_intent(message)
    m = (message or "")

    if intent == "greet":
        return ("Hello! I can help you find buses, check fares, track your bus live, "
                "and predict arrival times. Try: 'Which bus is cheapest from "
                "Vizianagaram to Visakhapatnam?'")

    if not buses:
        return ("I could not find any buses matching your query right now. "
                "Please check the Search Buses page for live availability.")

    if intent == "cheapest":
        b = min(buses, key=lambda x: float(x.get("fare", 1e9)))
        return (f"Bus {b.get('bus_number')} has the lowest fare among the available "
                f"buses at Rs.{b.get('fare')} ({b.get('operator')}, "
                f"departs {b.get('departure_time')}).")

    if intent == "earliest":
        b = min(buses, key=lambda x: str(x.get("departure_time", "99:99")))
        return (f"The earliest bus is {_fmt_bus(b)}.")

    if intent == "before_time":
        hr = re.search(r"before\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", m.lower())
        limit = None
        if hr:
            h = int(hr.group(1)); mn = int(hr.group(2) or 0); ap = hr.group(3)
            if ap == "pm" and h < 12:
                h += 12
            if ap == "am" and h == 12:
                h = 0
            limit = h * 60 + mn

        def arr_min(b):
            try:
                h2, m2 = str(b.get("arrival_time", "23:59")).split(":")
                return int(h2) * 60 + int(m2)
            except Exception:
                return 24 * 60
        cands = [b for b in buses if limit is None or arr_min(b) <= limit]
        if not cands:
            return ("No buses arrive before that time on this corridor. "
                    "Try a later arrival or a different date.")
        names = ", ".join(f"{b.get('bus_number')} (arr {b.get('arrival_time')})" for b in cands[:4])
        return (f"I found {len(cands)} bus(es) arriving on time: {names}. "
                f"Top pick: {cands[0].get('bus_number')} at Rs.{cands[0].get('fare')}.")

    if intent == "most_seats":
        def avail(b):
            return int(b.get("total_seats", 40)) - len(b.get("booked_seats") or [])
        b = max(buses, key=avail)
        return (f"Bus {b.get('bus_number')} has the most available seats right now "
                f"({avail(b)} seats, fare Rs.{b.get('fare')}).")

    if intent == "track_bus":
        num = re.search(r"AP\s?\d[\w\d]*", m.upper())
        target = None
        if num:
            key = num.group(0).replace(" ", "")
            for b in buses:
                if str(b.get("bus_number", "")).replace(" ", "").upper() == key:
                    target = b
                    break
        target = target or buses[0]
        t = tracking.get(target.get("bus_number"), {})
        if t:
            return (f"Bus {target.get('bus_number')} is currently near "
                    f"{t.get('current_location', 'en route')} moving at "
                    f"{t.get('speed', '?')} km/h. Status: {t.get('status','-')}. "
                    f"Estimated arrival in ~{t.get('eta_minutes','?')} minutes.")
        return (f"Bus {target.get('bus_number')} status is "
                f"{target.get('status','ON_TIME')}, scheduled "
                f"{target.get('departure_time')} -> {target.get('arrival_time')}. "
                f"Live GPS will appear once the driver starts the trip.")

    if intent == "eta":
        b = buses[0]
        t = tracking.get(b.get("bus_number"), {})
        if t and t.get("eta_minutes") is not None:
            return (f"Estimated arrival for bus {b.get('bus_number')} is "
                    f"~{t.get('eta_minutes')} minutes (currently near "
                    f"{t.get('current_location','en route')}).")
        return (f"Bus {b.get('bus_number')} is scheduled to arrive at "
                f"{b.get('arrival_time')}. Live ETA appears once the trip starts.")

    if intent == "cancel_policy":
        return ("You can cancel free of charge up to 1 hour before departure "
                "from My Bookings. The refund is auto-credited and the seat "
                "becomes available again.")

    # default: search-style summary
    top = buses[:3]
    lines = "; ".join(f"{b.get('bus_number')} {b.get('departure_time')}->"
                      f"{b.get('arrival_time')} Rs.{b.get('fare')}" for b in top)
    src = buses[0].get("source", "")
    dst = buses[0].get("destination", "")
    return (f"On {src} -> {dst} I found {len(buses)} option(s): {lines}. "
            f"Want the cheapest or the earliest?")
