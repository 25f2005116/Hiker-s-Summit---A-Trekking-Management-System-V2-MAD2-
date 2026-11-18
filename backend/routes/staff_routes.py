from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Trek, Booking, User
from routes.decorators import role_required

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/assigned-treks", methods=["GET"])
@role_required("Staff")
def get_assigned_treks():
    staff_id = int(get_jwt_identity())
    
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).order_by(Trek.start_date.asc()).all()
    
    result = []
    for trek in treks:
        participant_count = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
        trek_dict = trek.to_dict()
        trek_dict["participant_count"] = participant_count
        result.append(trek_dict)

    return jsonify(result), 200


@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@role_required("Staff")
def get_trek_participants(trek_id):
    staff_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    if trek.assigned_staff_id != staff_id:
        return jsonify({"error": "Access Denied: You are not assigned to this trek"}), 403

    bookings = Booking.query.filter_by(trek_id=trek_id, status="Booked").all()
    participants = []
    for b in bookings:
        participants.append({
            "booking_id": b.id,
            "user_id": b.user_id,
            "username": b.user.username if b.user else "Unknown",
            "contact_details": b.user.contact_details if b.user else "",
            "booking_date": b.booking_date.strftime("%Y-%m-%d"),
            "status": b.status
        })

    return jsonify({
        "trek": trek.to_dict(),
        "participants": participants,
        "total_participants": len(participants)
    }), 200
