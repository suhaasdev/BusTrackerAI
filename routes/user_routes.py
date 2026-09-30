from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash
from utils.database import get_db, serialize
from utils.responses import success, error
from utils.decorators import jwt_required_any, current_user

user_bp = Blueprint("users", __name__)


def _me(db, uid):
    for u in db.users.find({}):
        if str(u.get("_id")) == str(uid):
            return u
    return None


@user_bp.get("/api/users/profile")
@jwt_required_any
def get_profile():
    uid, _, _ = current_user()
    db, _ = get_db()
    u = _me(db, uid)
    if not u:
        return error("User not found.", "NOT_FOUND", 404)
    d = serialize(u)
    d.pop("password_hash", None)
    # booking stats
    bks = [b for b in db.bookings.find({}) if str(b.get("user_id")) == str(uid)]
    d["stats"] = {"total": len(bks),
                  "active": sum(1 for b in bks if b.get("status") == "CONFIRMED"),
                  "cancelled": sum(1 for b in bks if b.get("status") == "CANCELLED")}
    return success({"user": d})


@user_bp.put("/api/users/profile")
@jwt_required_any
def update_profile():
    uid, _, _ = current_user()
    data = request.get_json(force=True, silent=True) or {}
    db, _ = get_db()
    u = _me(db, uid)
    if not u:
        return error("User not found.", "NOT_FOUND", 404)
    patch = {}
    if data.get("name"):
        patch["name"] = str(data["name"]).strip()
    if data.get("phone"):
        patch["phone"] = str(data["phone"]).strip()
    if patch:
        db.users.update_one({"_id": u["_id"]}, {"$set": patch})
    return success({}, "Profile updated.")


@user_bp.put("/api/users/password")
@jwt_required_any
def change_password():
    uid, _, _ = current_user()
    data = request.get_json(force=True, silent=True) or {}
    db, _ = get_db()
    u = _me(db, uid)
    if not u:
        return error("User not found.", "NOT_FOUND", 404)
    if not check_password_hash(u.get("password_hash", ""), data.get("current_password", "")):
        return error("Current password is incorrect.", "INVALID", 401)
    if len(data.get("new_password", "")) < 6:
        return error("New password must be 6+ characters.", "VALIDATION", 422)
    db.users.update_one({"_id": u["_id"]},
                        {"$set": {"password_hash": generate_password_hash(data["new_password"])}})
    return success({}, "Password changed.")


@user_bp.get("/api/notifications")
@jwt_required_any
def notifications():
    uid, _, _ = current_user()
    db, _ = get_db()
    try:
        notes = [serialize(n) for n in db.notifications.find({"user_id": str(uid)})]
    except Exception:
        notes = []
    notes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return success({"notifications": notes[:20]})
