from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from utils.database import get_db, serialize
from utils.responses import success, error
from utils.validators import valid_email, valid_phone
from utils.decorators import current_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/auth/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    role = (data.get("role") or "passenger").strip().lower()
    if role not in ("passenger", "driver"):
        role = "passenger"
    if not name or not email or not password:
        return error("Name, email and password are required.", "VALIDATION", 422)
    if not valid_email(email):
        return error("Invalid email address.", "VALIDATION", 422)
    if phone and not valid_phone(phone):
        return error("Invalid phone number.", "VALIDATION", 422)
    if len(password) < 6:
        return error("Password must be at least 6 characters.", "VALIDATION", 422)
    db, _ = get_db()
    if db.users.find_one({"email": email}):
        return error("Email already registered.", "DUPLICATE_EMAIL", 409)
    user = {
        "name": name, "email": email, "phone": phone,
        "password_hash": generate_password_hash(password),
        "role": role, "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }
    rid = db.users.insert_one(user).inserted_id
    return success({"user_id": str(rid), "role": role}, "Registered successfully. Please login.", 201)


@auth_bp.post("/api/auth/login")
def login():
    from flask import session
    from config import Config
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return error("Email and password are required.", "VALIDATION", 422)
    db, _ = get_db()
    user = db.users.find_one({"email": email})
    if not user or not check_password_hash(user.get("password_hash", ""), password):
        return error("Invalid email or password.", "INVALID_CREDENTIALS", 401)
    if user.get("status") != "active":
        return error("Account is disabled. Contact support.", "DISABLED", 403)
    uid = str(user["_id"])
    token = create_access_token(identity=uid,
                                additional_claims={"role": user.get("role", "passenger"),
                                                   "name": user.get("name", "")},
                                expires_delta=timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS))
    session["user_id"] = uid
    session["role"] = user.get("role", "passenger")
    session["name"] = user.get("name", "")
    u = serialize(user)
    u.pop("password_hash", None)
    return success({"token": token, "user": u, "role": u.get("role")}, "Login successful.")


@auth_bp.post("/api/auth/logout")
def logout():
    from flask import session
    session.clear()
    return success({}, "Logged out.")


@auth_bp.get("/api/auth/me")
def me():
    uid, role, _ = current_user()
    if not uid:
        return error("Not authenticated.", "UNAUTHORIZED", 401)
    db, _ = get_db()
    user = None
    # memory store uses string ids; mongo may use ObjectId — try both
    user = db.users.find_one({"_id": uid})
    if not user:
        # brute force scan
        for u in db.users.find({}):
            if str(u.get("_id")) == str(uid):
                user = u
                break
    if not user:
        return error("User not found.", "NOT_FOUND", 404)
    u = serialize(user)
    u.pop("password_hash", None)
    return success({"user": u})
