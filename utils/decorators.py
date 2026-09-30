from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt


def jwt_required_any(fn):
    """Accept JWT via Authorization header OR session (for server-rendered pages)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Try JWT first
        try:
            verify_jwt_in_request(optional=True)
            ident = get_jwt_identity()
            if ident:
                return fn(*args, **kwargs)
        except Exception:
            pass
        # Fall back to session
        from flask import session
        if session.get("user_id"):
            return fn(*args, **kwargs)
        return jsonify({"success": False, "message": "Authentication required", "error": "UNAUTHORIZED"}), 401
    return wrapper


def current_user():
    """Return (user_id, role, claims) from JWT or session."""
    try:
        verify_jwt_in_request(optional=True)
        ident = get_jwt_identity()
        if ident:
            claims = get_jwt()
            return ident, claims.get("role", "passenger"), claims
    except Exception:
        pass
    from flask import session
    if session.get("user_id"):
        return session.get("user_id"), session.get("role", "passenger"), {}
    return None, None, {}


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            uid, role, _ = current_user()
            if not uid:
                return jsonify({"success": False, "message": "Authentication required", "error": "UNAUTHORIZED"}), 401
            if role not in roles:
                return jsonify({"success": False, "message": "Forbidden for your role", "error": "FORBIDDEN"}), 403
            return fn(*a, **kw)
        return wrapper
    return deco


def login_required_page(role=None):
    """Decorator for server-rendered pages: redirect to /login if not authed."""
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            from flask import session, redirect, url_for, request
            uid, r, _ = current_user()
            if not uid:
                return redirect(url_for("pages.login", next=request.path))
            if role and r != role and r not in (role if isinstance(role, (list, tuple)) else [role]):
                return redirect(url_for("pages.login", next=request.path))
            return fn(*a, **kw)
        return wrapper
    return deco
