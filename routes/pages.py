from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from utils.decorators import login_required_page, current_user
from utils.database import get_db, serialize
from werkzeug.security import check_password_hash, generate_password_hash

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def home():
    return render_template("index.html")


@pages_bp.get("/about")
def about():
    return render_template("about.html")


@pages_bp.get("/contact")
def contact():
    return render_template("contact.html")


@pages_bp.get("/login")
def login():
    return render_template("login.html")


@pages_bp.get("/register")
def register():
    return render_template("register.html")


@pages_bp.get("/dashboard")
@login_required_page()
def dashboard():
    uid, role, _ = current_user()
    if role == "driver":
        return redirect(url_for("pages.driver_dashboard"))
    if role == "admin":
        return redirect(url_for("pages.admin_dashboard"))
    return render_template("dashboard.html")


@pages_bp.get("/search")
def search():
    return render_template("search.html")


@pages_bp.get("/bus/<bus_id>")
def bus_details(bus_id):
    return render_template("bus_details.html", bus_id=bus_id)


@pages_bp.get("/tracking/<bus_id>")
def tracking(bus_id):
    return render_template("tracking.html", bus_id=bus_id)


@pages_bp.get("/track")
def track_general():
    return render_template("tracking.html", bus_id="")


@pages_bp.get("/seats/<bus_id>")
@login_required_page()
def seats(bus_id):
    return render_template("seats.html", bus_id=bus_id)


@pages_bp.get("/bookings")
@login_required_page()
def bookings():
    return render_template("bookings.html")


@pages_bp.get("/booking/<booking_id>")
@login_required_page()
def ticket(booking_id):
    return render_template("ticket.html", booking_id=booking_id)


@pages_bp.get("/profile")
@login_required_page()
def profile():
    return render_template("profile.html")


@pages_bp.get("/ai-assistant")
def ai_assistant():
    return render_template("ai_assistant.html")


# ---- driver pages ----
@pages_bp.get("/driver/login")
def driver_login():
    return render_template("driver_login.html")


@pages_bp.get("/driver/dashboard")
@login_required_page(role="driver")
def driver_dashboard():
    return render_template("driver_dashboard.html")


@pages_bp.get("/admin/dashboard")
@login_required_page(role="admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")


@pages_bp.get("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("pages.home"))
