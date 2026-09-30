"""Seed demo data: routes, buses, users (passengers + drivers), tracking."""
from datetime import datetime
from werkzeug.security import generate_password_hash


def seed():
    from utils.database import get_db
    db, mem = get_db()
    if db.buses.count_documents({}) >= 3 and db.users.count_documents({}) >= 2:
        print(f"seed: already has data (db={'memory' if mem else 'mongodb'}), skipping.")
        return

    routes = [
        {"source": "Vizianagaram", "destination": "Visakhapatnam",
         "stops": ["Vizianagaram", "Gajapathinagaram", "Pusapatirega", "Visakhapatnam"],
         "distance_km": 65, "estimated_duration_minutes": 90, "corridor": "NH-26 Express Corridor"},
        {"source": "Visakhapatnam", "destination": "Vizianagaram",
         "stops": ["Visakhapatnam", "Pusapatirega", "Gajapathinagaram", "Vizianagaram"],
         "distance_km": 65, "estimated_duration_minutes": 95, "corridor": "NH-26 Express Corridor"},
        {"source": "Vizianagaram", "destination": "Srikakulam",
         "stops": ["Vizianagaram", "Rajam", "Srikakulam"],
         "distance_km": 55, "estimated_duration_minutes": 80, "corridor": "State Highway"},
        {"source": "Visakhapatnam", "destination": "Anakapalle",
         "stops": ["Visakhapatnam", "Gajuwaka", "Anakapalle"],
         "distance_km": 28, "estimated_duration_minutes": 45, "corridor": "Suburban Corridor S-2"},
        {"source": "Visakhapatnam", "destination": "Vijayawada",
         "stops": ["Visakhapatnam", "Anakapalle", "Eluru", "Vijayawada"],
         "distance_km": 350, "estimated_duration_minutes": 420, "corridor": "NH-16 Express Way"},
    ]
    route_ids = []
    for r in routes:
        if db.routes.find_one({"source": r["source"], "destination": r["destination"]}):
            ex = db.routes.find_one({"source": r["source"], "destination": r["destination"]})
            route_ids.append(str(ex["_id"]))
        else:
            route_ids.append(str(db.routes.insert_one(r).inserted_id))

    buses = [
        {"bus_number": "AP31BT101", "operator": "ABC Travels", "bus_name": "AP Express",
         "bus_type": "AC Seater", "source": "Vizianagaram", "destination": "Visakhapatnam",
         "route_id": route_ids[0], "departure_time": "08:30", "arrival_time": "10:00",
         "fare": 120, "total_seats": 40, "status": "ON_TIME"},
        {"bus_number": "AP35TX402", "operator": "Sri Krishna Exp", "bus_name": "City Bus",
         "bus_type": "Non-AC Seater", "source": "Vizianagaram", "destination": "Visakhapatnam",
         "route_id": route_ids[0], "departure_time": "09:00", "arrival_time": "10:45",
         "fare": 85, "total_seats": 44, "status": "DELAYED"},
        {"bus_number": "AP31ER808", "operator": "APSRTC", "bus_name": "Super Luxury",
         "bus_type": "AC Sleeper", "source": "Vizianagaram", "destination": "Visakhapatnam",
         "route_id": route_ids[0], "departure_time": "09:45", "arrival_time": "11:15",
         "fare": 150, "total_seats": 36, "status": "ON_TIME"},
        {"bus_number": "AP31MK109", "operator": "Coastal Metro", "bus_name": "Metro Shuttle",
         "bus_type": "Non-AC Seater", "source": "Visakhapatnam", "destination": "Anakapalle",
         "route_id": route_ids[3], "departure_time": "10:15", "arrival_time": "11:00",
         "fare": 60, "total_seats": 35, "status": "ON_TIME"},
        {"bus_number": "AP30VK220", "operator": "City Travels", "bus_name": "Vizag Return",
         "bus_type": "AC Seater", "source": "Visakhapatnam", "destination": "Vizianagaram",
         "route_id": route_ids[1], "departure_time": "14:00", "arrival_time": "15:35",
         "fare": 120, "total_seats": 40, "status": "ON_TIME"},
        {"bus_number": "AP16GH505", "operator": "RTC Super Luxury", "bus_name": "Coastal Express",
         "bus_type": "AC Sleeper", "source": "Visakhapatnam", "destination": "Vijayawada",
         "route_id": route_ids[4], "departure_time": "21:00", "arrival_time": "04:00",
         "fare": 450, "total_seats": 36, "status": "ON_TIME"},
        {"bus_number": "AP35SK310", "operator": "Sri Krishna Exp", "bus_name": "Srikakulam Link",
         "bus_type": "Express", "source": "Vizianagaram", "destination": "Srikakulam",
         "route_id": route_ids[2], "departure_time": "07:00", "arrival_time": "08:20",
         "fare": 90, "total_seats": 40, "status": "ON_TIME"},
        {"bus_number": "AP31BT102", "operator": "ABC Travels", "bus_name": "AP Evening",
         "bus_type": "AC Seater", "source": "Visakhapatnam", "destination": "Vizianagaram",
         "route_id": route_ids[1], "departure_time": "18:00", "arrival_time": "19:35",
         "fare": 120, "total_seats": 40, "status": "ON_TIME"},
    ]
    bus_oids = {}
    for b in buses:
        ex = db.buses.find_one({"bus_number": b["bus_number"]})
        if ex:
            bus_oids[b["bus_number"]] = str(ex["_id"])
        else:
            bus_oids[b["bus_number"]] = str(db.buses.insert_one(b).inserted_id)

    users = [
        {"name": "Demo Passenger", "email": "user@bustrackerai.edu", "phone": "9876543210",
         "password": "Commuter#2025", "role": "passenger"},
        {"name": "Rahul Sharma", "email": "rahul@example.com", "phone": "9876543211",
         "password": "password123", "role": "passenger"},
        {"name": "Sneha Varma", "email": "sneha@example.com", "phone": "9876543212",
         "password": "password123", "role": "passenger"},
        {"name": "K. Appa Rao (Driver)", "email": "driver@bustrackerai.edu", "phone": "9848022319",
         "password": "Driver#2025", "role": "driver"},
        {"name": "K. Ramana (Driver)", "email": "ramana@example.com", "phone": "9848022320",
         "password": "password123", "role": "driver"},
    ]
    driver_ids = {}
    for u in users:
        if db.users.find_one({"email": u["email"]}):
            ex = db.users.find_one({"email": u["email"]})
            if u["role"] == "driver":
                driver_ids[u["email"]] = str(ex["_id"])
            continue
        doc = {"name": u["name"], "email": u["email"], "phone": u["phone"],
               "password_hash": generate_password_hash(u["password"]),
               "role": u["role"], "status": "active",
               "created_at": datetime.utcnow().isoformat()}
        nid = str(db.users.insert_one(doc).inserted_id)
        if u["role"] == "driver":
            driver_ids[u["email"]] = nid

    # assign buses to drivers
    assigns = [("driver@bustrackerai.edu", "AP31BT101"), ("ramana@example.com", "AP35TX402")]
    for email, bno in assigns:
        did = driver_ids.get(email)
        if not did:
            ex = db.users.find_one({"email": email})
            did = str(ex["_id"]) if ex else None
        if did:
            for b in db.buses.find({}):
                if b.get("bus_number") == bno:
                    db.buses.update_one({"_id": b["_id"]}, {"$set": {"driver_id": did}})
                    break

    # simulated tracking for main bus
    main_oid = bus_oids.get("AP31BT101")
    if main_oid and db.tracking.count_documents({"bus_id": main_oid}) == 0:
        db.tracking.insert_one({
            "bus_id": main_oid, "bus_number": "AP31BT101",
            "latitude": 18.1219, "longitude": 83.4024,
            "current_location": "Gajapathinagaram Bypass", "speed": 42,
            "status": "ON_TIME", "eta_minutes": 35, "progress_ratio": 0.38,
            "simulated": True, "updated_at": datetime.utcnow().isoformat()})

    print(f"seed: done (db={'memory' if mem else 'mongodb'}).")
    print("  passenger: user@bustrackerai.edu / Commuter#2025")
    print("  driver:    driver@bustrackerai.edu / Driver#2025")


if __name__ == "__main__":
    seed()
