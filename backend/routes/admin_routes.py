from flask import Blueprint, request, jsonify
from database import db
from models import User, Trek, Booking
from routes.decorators import role_required
from cache import invalidate_treks_cache

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard-stats", methods=["GET"])
@role_required("Admin")
def get_dashboard_stats():
    """Admin dashboard stats: total treks, total users and staffs, total bookings."""
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="User").count()
    total_staff = User.query.filter_by(role="Staff").count()
    total_bookings = Booking.query.count()

    return jsonify({
        "total_treks": total_treks,
        "total_users": total_users,
        "total_staff": total_staff,
        "total_bookings": total_bookings
    }), 200


@admin_bp.route("/users", methods=["GET"])
@role_required("Admin")
def get_users():
    users = User.query.filter_by(role="User").order_by(User.id.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.route("/staff", methods=["GET"])
@role_required("Admin")
def get_staff():
    staff_members = User.query.filter_by(role="Staff").order_by(User.id.desc()).all()
    return jsonify([s.to_dict() for s in staff_members]), 200


@admin_bp.route("/staff", methods=["POST"])
@role_required("Admin")
def create_staff():
    """Admin adds and manages trek staff (Staff cannot self-register)."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    contact_details = data.get("contact_details", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    new_staff = User(
        username=username,
        role="Staff",
        status="Approved",
        contact_details=contact_details
    )
    new_staff.set_password(password)

    db.session.add(new_staff)
    db.session.commit()

    return jsonify({
        "message": "Staff member created successfully",
        "staff": new_staff.to_dict()
    }), 201


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["PUT"])
@role_required("Admin")
def toggle_user_status(user_id):
    """Deactivate or blacklist users or staff."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == "Admin":
        return jsonify({"error": "Cannot blacklist Administrator"}), 400

    user.status = "Blacklisted" if user.status == "Approved" else "Approved"
    db.session.commit()

    return jsonify({
        "message": f"User status set to {user.status}",
        "user": user.to_dict()
    }), 200


@admin_bp.route("/treks/<int:trek_id>/assign-staff", methods=["PUT"])
@role_required("Admin")
def assign_staff(trek_id):
    """Assign staff to treks."""
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    data = request.get_json() or {}
    staff_id = data.get("staff_id")

    if staff_id:
        staff = User.query.filter_by(id=staff_id, role="Staff", status="Approved").first()
        if not staff:
            return jsonify({"error": "Staff member not found or is blacklisted"}), 404
        trek.assigned_staff_id = staff.id
    else:
        trek.assigned_staff_id = None

    db.session.commit()
    invalidate_treks_cache()

    return jsonify({
        "message": "Staff assignment updated",
        "trek": trek.to_dict()
    }), 200


@admin_bp.route("/bookings", methods=["GET"])
@role_required("Admin")
def get_all_bookings():
    """Allow admin to view all historical trekking data and bookings."""
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@admin_bp.route("/search", methods=["GET"])
@role_required("Admin")
def admin_search():
    """Search users, staff, or treks."""
    query_str = request.args.get("q", "").strip()
    if not query_str:
        return jsonify({"treks": [], "users": [], "staff": []}), 200

    if query_str.isdigit():
        target_id = int(query_str)
        treks = Trek.query.filter_by(id=target_id).all()
        users = User.query.filter_by(id=target_id, role="User").all()
        staff = User.query.filter_by(id=target_id, role="Staff").all()
    else:
        treks = Trek.query.filter(
            (Trek.trek_name.ilike(f"%{query_str}%")) | (Trek.location.ilike(f"%{query_str}%"))
        ).all()
        users = User.query.filter(
            (User.username.ilike(f"%{query_str}%")), User.role == "User"
        ).all()
        staff = User.query.filter(
            (User.username.ilike(f"%{query_str}%")), User.role == "Staff"
        ).all()

    return jsonify({
        "treks": [t.to_dict() for t in treks],
        "users": [u.to_dict() for u in users],
        "staff": [s.to_dict() for s in staff]
    }), 200


@admin_bp.route("/trigger-reminders", methods=["POST"])
@role_required("Admin")
def trigger_reminders_admin():
    from tasks.reminders import process_daily_reminders
    results = process_daily_reminders()
    return jsonify({
        "message": f"Daily Reminders executed! Dispatched {len(results)} reminder(s) for upcoming treks.",
        "count": len(results),
        "reminders": results
    }), 200


@admin_bp.route("/trigger-monthly-report", methods=["POST"])
@role_required("Admin")
def trigger_monthly_report_admin():
    from tasks.reports import generate_monthly_report
    report = generate_monthly_report()
    return jsonify({
        "message": f"Monthly Activity Report generated for {report['month']}!",
        "filename": report["filename"],
        "view_url": f"/api/admin/reports/{report['filename']}"
    }), 200


@admin_bp.route("/reports/<filename>", methods=["GET"])
def view_monthly_report(filename):
    from flask import send_from_directory
    from config import Config
    return send_from_directory(Config.REPORTS_FOLDER, filename)

