"""BusTrackerAI — Flask entry point (Python only, no Java)."""
import os
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    CORS(app, supports_credentials=True)
    JWTManager(app)

    from routes.auth_routes import auth_bp
    from routes.bus_routes import bus_bp, route_bp
    from routes.booking_routes import booking_bp
    from routes.trip_routes import trip_bp
    from routes.tracking_routes import tracking_bp
    from routes.ai_routes import ai_bp
    from routes.user_routes import user_bp
    from routes.pages import pages_bp
    from routes.admin_routes import admin_bp

    for bp in (auth_bp, bus_bp, route_bp, booking_bp, trip_bp, tracking_bp, ai_bp, user_bp, pages_bp, admin_bp):
        app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        from utils.database import get_db
        try:
            _, mem = get_db()
            db_mode = "memory (MongoDB unreachable)" if mem else "mongodb"
        except Exception as e:
            db_mode = f"error: {e}"
        return jsonify({"success": True, "service": "BusTrackerAI Flask API",
                        "db": db_mode, "backend": "python-flask"})

    @app.errorhandler(404)
    def nf(e):
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Not found", "error": "NOT_FOUND"}), 404
        return e

    @app.errorhandler(500)
    def se(e):
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Internal error. Please try again.",
                            "error": "SERVER_ERROR"}), 500
        return e

    return app


app = create_app()

# Auto-seed on import too (production servers like gunicorn import the
# app instead of running __main__). Safe: seed() skips when data exists.
try:
    from scripts.seed_database import seed
    seed()
except Exception as e:
    print("seed skipped:", e)

if __name__ == "__main__":
    # auto-seed on first run (safe: skips if data exists)
    try:
        from scripts.seed_database import seed
        seed()
    except Exception as e:
        print("seed skipped:", e)
    port = int(os.getenv("PORT", "5000"))
    print(f"\n  BusTrackerAI running at http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
