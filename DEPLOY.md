# Deploying BusTrackerAI (any host)

The app is deployment-ready: `Procfile`, `render.yaml`, port-flexible `Dockerfile`,
`requirements.txt` (gunicorn), and auto-seed on boot. It needs ONE environment
variable on the host: `MONGO_URI` (Atlas connection string; without it the app
runs in demo memory mode).

## Option A — Hugging Face Spaces (free, no card) — recommended

1. Create a Space at https://huggingface.co/new-space — name `BusTrackerAI`, SDK **Docker**, Public.
2. Push this repo to the Space (replace USER):
   ```
   git remote add space https://USER:hf_TOKEN@huggingface.co/spaces/USER/BusTrackerAI
   git push space main
   ```
   The Dockerfile already listens on `${PORT:-7860}` (Spaces' port). Live URL:
   `https://huggingface.co/spaces/USER/BusTrackerAI`

## Option B — Render (free)

Click: `https://render.com/deploy?repo=https://github.com/suhaasdev/BusTrackerAI`
— `render.yaml` pre-fills build/start. Add `MONGO_URI`, Deploy.

## Option C — Railway (free trial)

Railway → New Project → Deploy from GitHub → `suhaasdev/BusTrackerAI`.
Auto-detects `Procfile`. Add `MONGO_URI`. Done.

## Demo accounts (seeded automatically on first boot)

- Passenger: `user@bustrackerai.edu` / `Commuter#2025`
- Driver: `driver@bustrackerai.edu` / `Driver#2025`
