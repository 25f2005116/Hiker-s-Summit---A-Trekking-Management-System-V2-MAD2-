import os
from datetime import date
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Booking, Trek, User
from cache import invalidate_treks_cache
from routes.decorators import role_required
from config import Config
from tasks.exports import export_user_bookings_csv

booking_bp = Blueprint("bookings", __name__)

@booking_bp.route("", methods=["POST"])
@role_required("User")
def book_trek():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    trek_id = data.get("trek_id")

    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    # Allow booking only when trek status is Open
    if trek.status != "Open":
        return jsonify({"error": f"Trek is currently {trek.status} and not accepting bookings"}), 400

    # Prevent overbooking beyond available slots
    if trek.available_slots <= 0:
        return jsonify({"error": "No available slots left for this trek"}), 400

    # Prevent duplicate bookings for same trek
    existing_booking = Booking.query.filter_by(
        user_id=user_id,
        trek_id=trek_id,
        status="Booked"
    ).first()

    if existing_booking:
        return jsonify({"error": "You have already booked this trek"}), 409

    new_booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        booking_date=date.today(),
        status="Booked"
    )

    trek.available_slots -= 1
    db.session.add(new_booking)
    db.session.commit()

    invalidate_treks_cache()

    return jsonify({
        "message": "Trek booked successfully!",
        "booking": new_booking.to_dict()
    }), 201


@booking_bp.route("/my", methods=["GET"])
@role_required("User")
def get_my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.id.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@booking_bp.route("/<int:booking_id>/cancel", methods=["PUT"])
@role_required("User")
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    if booking.user_id != user_id:
        return jsonify({"error": "Access Denied"}), 403

    if booking.status != "Booked":
        return jsonify({"error": f"Booking cannot be cancelled because it is already {booking.status}"}), 400

    booking.status = "Cancelled"
    
    # Restore slot
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1

    db.session.commit()
    invalidate_treks_cache()

    return jsonify({
        "message": "Booking cancelled successfully",
        "booking": booking.to_dict()
    }), 200


@booking_bp.route("/history", methods=["GET"])
@role_required("User")
def get_trekking_history():
    """User can view booking status and trekking history."""
    user_id = int(get_jwt_identity())
    bookings = Booking.query.join(Trek).filter(
        Booking.user_id == user_id,
        Booking.status == "Booked",
        Trek.status == "Completed"
    ).all()

    return jsonify([b.to_dict() for b in bookings]), 200


@booking_bp.route("/export-csv", methods=["POST"])
@role_required("User")
def trigger_csv_export():
    """User Triggered Async Job - Export Booking History as CSV via Celery."""
    user_id = int(get_jwt_identity())
    task = export_user_bookings_csv.delay(user_id)
    return jsonify({
        "message": "CSV export batch job triggered",
        "task_id": task.id
    }), 202


@booking_bp.route("/export-status/<task_id>", methods=["GET"])
@role_required("User")
def check_export_status(task_id):
    from celery_app import celery
    res = celery.AsyncResult(task_id)
    if res.ready():
        return jsonify({
            "status": res.status,
            "ready": True,
            "download_url": f"/api/bookings/download-export/{res.result}"
        }), 200
    return jsonify({"status": res.status, "ready": False}), 200


@booking_bp.route("/download-export/<filename>", methods=["GET"])
def download_export(filename):
    return send_from_directory(Config.EXPORTS_FOLDER, filename, as_attachment=True)
