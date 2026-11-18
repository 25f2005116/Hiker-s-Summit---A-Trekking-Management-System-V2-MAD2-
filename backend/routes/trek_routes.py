from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from database import db
from models import Trek, User
from cache import get_cache, set_cache, invalidate_treks_cache
from routes.decorators import role_required

trek_bp = Blueprint("treks", __name__)

@trek_bp.route("", methods=["GET"])
def get_treks():
    difficulty = request.args.get("difficulty", "").strip()
    location = request.args.get("location", "").strip()
    max_duration = request.args.get("duration", "").strip()
    status_filter = request.args.get("status", "").strip()
    
    # Check cache for public queries
    cache_key = f"treks:list:diff={difficulty}:loc={location}:dur={max_duration}:stat={status_filter}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return jsonify(cached_data), 200

    query = Trek.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    else:
        # Default for visitors / users is Open treks
        query = query.filter_by(status="Open")

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    if max_duration and max_duration.isdigit():
        query = query.filter(Trek.duration <= int(max_duration))

    treks = query.order_by(Trek.start_date.asc()).all()
    result = [t.to_dict() for t in treks]

    # Cache for 5 minutes (300 seconds)
    set_cache(cache_key, result, timeout_seconds=300)

    return jsonify(result), 200


@trek_bp.route("/all", methods=["GET"])
@role_required("Admin")
def get_all_treks_admin():
    """Admin-only endpoint to view all treks regardless of status."""
    treks = Trek.query.order_by(Trek.id.desc()).all()
    return jsonify([t.to_dict() for t in treks]), 200


@trek_bp.route("/<int:trek_id>", methods=["GET"])
def get_trek(trek_id):
    cache_key = f"treks:detail:{trek_id}"
    cached_trek = get_cache(cache_key)
    if cached_trek is not None:
        return jsonify(cached_trek), 200

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    trek_data = trek.to_dict()
    set_cache(cache_key, trek_data, timeout_seconds=300)
    return jsonify(trek_data), 200


@trek_bp.route("", methods=["POST"])
@role_required("Admin")
def create_trek():
    data = request.get_json() or {}
    
    trek_name = data.get("trek_name", "").strip()
    location = data.get("location", "").strip()
    difficulty = data.get("difficulty", "Moderate").strip()
    duration = data.get("duration")
    available_slots = data.get("available_slots")
    status = data.get("status", "Open").strip()
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")

    if not all([trek_name, location, duration, available_slots, start_date_str, end_date_str]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    if end_date < start_date:
        return jsonify({"error": "End date cannot be earlier than start date"}), 400

    # Duplicate check: same trek name and start date
    if Trek.query.filter_by(trek_name=trek_name, start_date=start_date).first():
        return jsonify({"error": "A trek with this name and start date already exists"}), 409

    slots = int(available_slots)
    new_trek = Trek(
        trek_name=trek_name,
        location=location,
        difficulty=difficulty,
        duration=int(duration),
        total_slots=slots,
        available_slots=slots,
        status=status,
        start_date=start_date,
        end_date=end_date,
        assigned_staff_id=data.get("assigned_staff_id") or None
    )

    db.session.add(new_trek)
    db.session.commit()

    # Invalidate cache
    invalidate_treks_cache()

    return jsonify({"message": "Trek created successfully", "trek": new_trek.to_dict()}), 201


@trek_bp.route("/<int:trek_id>", methods=["PUT"])
@role_required("Admin")
def update_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    data = request.get_json() or {}

    if "trek_name" in data:
        trek.trek_name = data["trek_name"]
    if "location" in data:
        trek.location = data["location"]
    if "difficulty" in data:
        trek.difficulty = data["difficulty"]
    if "duration" in data:
        trek.duration = int(data["duration"])
    if "available_slots" in data:
        slots_val = int(data["available_slots"])
        trek.available_slots = slots_val
        trek.total_slots = slots_val
    if "status" in data:
        trek.status = data["status"]
    if "start_date" in data:
        trek.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if "end_date" in data:
        trek.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    if "assigned_staff_id" in data:
        trek.assigned_staff_id = data["assigned_staff_id"] or None

    db.session.commit()
    invalidate_treks_cache()

    return jsonify({"message": "Trek updated successfully", "trek": trek.to_dict()}), 200


@trek_bp.route("/<int:trek_id>", methods=["DELETE"])
@role_required("Admin")
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    db.session.delete(trek)
    db.session.commit()
    invalidate_treks_cache()

    return jsonify({"message": "Trek deleted successfully"}), 200


@trek_bp.route("/<int:trek_id>/staff-update", methods=["PUT"])
@role_required("Staff")
def staff_update_trek(trek_id):
    staff_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    if trek.assigned_staff_id != staff_id:
        return jsonify({"error": "You are not assigned to manage this trek"}), 403

    data = request.get_json() or {}

    if "available_slots" in data:
        slots_val = int(data["available_slots"])
        trek.available_slots = slots_val
        trek.total_slots = slots_val
    if "status" in data:
        # Staff can set Open, Closed, Started, Completed
        new_status = data["status"]
        if new_status in ["Open", "Closed", "Started", "Completed"]:
            trek.status = new_status

    db.session.commit()
    invalidate_treks_cache()

    return jsonify({"message": "Trek updated by staff", "trek": trek.to_dict()}), 200
