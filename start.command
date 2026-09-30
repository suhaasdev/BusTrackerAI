#!/bin/bash
# Double-click to run BusTrackerAI like a desktop app (macOS).
cd "$(dirname "$0")"
python3 -m venv venv 2>/dev/null
source venv/bin/activate
pip install -q -r requirements.txt
export PORT=8000
python3 -c "import urllib.request; " 2>/dev/null
(sleep 2 && open http://127.0.0.1:8000) &
python3 app.py
