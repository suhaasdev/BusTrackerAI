#!/bin/bash
# BusTrackerAI auto-run wrapper (used by LaunchAgent).
cd "/Users/suhaas/Youtube/venu csp" || exit 1
export PORT=8000
exec /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 app.py
