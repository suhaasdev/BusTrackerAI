# BusTrackerAI — AI-Based Smart Bus Tracking & Ticket Booking System

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/suhaasdev/BusTrackerAI)

**Web app · Passenger + Driver roles · Python Flask REST API · MongoDB · No Java anywhere.**

Passengers search buses, view routes, track live, pick seats, book tickets, manage bookings and chat with an AI assistant.
Drivers log in, view assigned bus/route, start/end trips, share GPS location, view passenger manifests and report issues.

## Tech stack
| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JS (ES6), Bootstrap 5, Leaflet/OpenStreetMap |
| Backend | Python 3 + Flask (REST API), Flask-JWT-Extended, Werkzeug hashing |
| Database | MongoDB via PyMongo (transparent in-memory demo fallback) |
| AI | Python rule-based prototypes: ETA predictor, delay classifier, recommendation scorer, intent-based assistant (ML-ready) |

## Colour palette
`#155EEF` primary · `#0B1F3A` navy · `#38BDF8` sky · `#10B981` success/available · `#F59E0B` warning/delay · `#EF4444` danger · `#F8FAFC` bg · `#7C3AED` AI-only purple. See `static/css/style.css`.

## Deploy (free: Render + MongoDB Atlas)

1. **Database (free):** create a free M0 cluster at https://cloud.mongodb.com → Network Access → allow `0.0.0.0/0` → copy the connection string
   (looks like `mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/bustrackerai`).
2. **Web service (free):** go to https://dashboard.render.com → New → Web Service → connect repo `suhaasdev/BusTrackerAI`
   (or click **Deploy to Render** above — `render.yaml` pre-fills everything).
   - Build: `pip install -r requirements.txt` · Start: `gunicorn app:app ...` (already set)
   - Environment → add `MONGO_URI` = your Atlas string (without it the app still runs in demo memory mode).
3. Deploy → open the `https://bustrackerai.onrender.com` URL. Demo data seeds automatically on first boot.
   Login with `user@bustrackerai.edu / Commuter#2025` (passenger) or `driver@bustrackerai.edu / Driver#2025` (driver).

> Note: free Render instances sleep when idle (first load takes ~1 min to wake). Single worker is configured so demo mode stays consistent; add Atlas for real persistence.

## Quick start (local)
```bash
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # edit MONGO_URI if needed
python scripts/seed_database.py   # optional (app.py auto-seeds too)
python app.py               # → http://127.0.0.1:5000
```

### MongoDB setup
- **With MongoDB:** install & start `mongod`, keep `MONGO_URI=mongodb://localhost:27017/bustrackerai`. Data persists.
- **Without MongoDB (demo):** app auto-falls back to an in-memory store — everything works, data resets on restart. The `/api/health` endpoint shows which mode is active.

### Demo accounts (seeded)
- Passenger: `user@bustrackerai.edu` / `Commuter#2025`
- Driver: `driver@bustrackerai.edu` / `Driver#2025`
- Admin: `admin@bustrackerai.edu` / `Admin#2025` → Fleet Control at `/admin/dashboard` (stats, users, buses CRUD, bookings, tracking console, analytics)

## Architecture
```
Browser (HTML/CSS/JS + fetch)
   ↓ HTTP
Flask REST API (routes/ → services/AI)
   ↓            ↓            ↓
MongoDB     AI services   Tracking (driver GPS / simulated)
users,buses,routes,bookings,trips,locations,notifications,ai_conversations
```

## API reference
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/auth/register | – | Register (role: passenger/driver) |
| POST | /api/auth/login | – | Login → JWT + session |
| POST | /api/auth/logout | – | Logout |
| GET | /api/auth/me | JWT/session | Current user |
| GET | /api/buses?source=&destination=&date=&bus_type=&sort= | – | Search buses + availability |
| GET | /api/buses/<id> | – | Bus detail + route + tracking |
| GET | /api/routes | – | All routes |
| POST | /api/bookings | passenger | Create booking (fare re-computed server-side, seat-lock checked) |
| GET | /api/bookings | passenger | My history |
| GET | /api/bookings/<id> | owner | Ticket detail |
| PUT | /api/bookings/<id>/cancel | owner | Cancel (1-hr window) + release seats |
| GET | /api/tracking/<bus> | – | Live location + ETA + delay |
| GET | /api/driver/assigned | driver | Assigned bus/route/trip |
| POST | /api/trips/start | driver | Start trip |
| POST | /api/trips/location | driver | GPS update {latitude,longitude,speed} |
| POST | /api/trips/end | driver | End trip |
| POST | /api/trips/report | driver | Report issue |
| GET | /api/driver/manifest | driver | Passenger manifest |
| POST | /api/ai/chat | – | {message} → grounded answer |
| POST | /api/ai/recommend | – | Top-3 heuristic recommendations |
| GET | /api/ai/eta/<bus> | – | ETA prediction |
| GET | /api/users/profile | JWT/session | Profile + stats |
| GET | /api/health | – | Service + DB mode |

All APIs return `{success, message, data}` or `{success:false, message, error}`.

## Pages
`/` home · `/about` `/contact` · `/login` `/register` · `/dashboard` · `/search` · `/bus/<id>` · `/track` `/tracking/<id>` · `/seats/<id>` · `/bookings` · `/booking/<id>` · `/profile` · `/ai-assistant` · `/driver/login` · `/driver/dashboard`

## AI honesty note
Current AI = **rule-based prototypes** (ETA = distance/speed; scoring = fare+duration+availability+time; chatbot = intent detection over live DB rows). No fake buses are ever invented — every answer is computed from real collections. Architecture is ready to swap in sklearn/XGBoost/LLM models later.

## Project structure
```
app.py config.py requirements.txt .env.example
routes/ auth, buses, bookings, trips(driver), tracking, ai, users, pages
ai/ eta_predictor, delay_predictor, recommendation_engine, travel_assistant
utils/ database (mongo+memory), responses, validators, decorators
templates/ base + 14 pages   static/css + static/js
scripts/seed_database.py
stitch_bustrackerai_web_platform/ (UI mock references)
```

## Testing
Manual checklist verified via Flask test client: register, login (passenger+driver), search, bus detail, booking, **duplicate-seat 409**, history, cancel+release, driver start/GPS/end, manifest, tracking+ETA, AI cheapest/track/before-10AM, all pages HTTP 200.
