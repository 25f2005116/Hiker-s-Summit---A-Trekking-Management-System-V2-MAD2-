from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'Admin', 'Staff', 'User'
    status = db.Column(db.String(20), nullable=False, default="Approved")  # 'Approved', 'Blacklisted'
    contact_details = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "status": self.status,
            "contact_details": self.contact_details or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }


class Trek(db.Model):
    __tablename__ = "trek"
    
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # 'Easy', 'Moderate', 'Hard'
    duration = db.Column(db.Integer, nullable=False)  # in days
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Open")  # 'Open', 'Closed', 'Started', 'Completed'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    assigned_staff = db.relationship("User", foreign_keys=[assigned_staff_id], backref="assigned_treks")
    bookings = db.relationship("Booking", backref="trek", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "trek_name": self.trek_name,
            "location": self.location,
            "difficulty": self.difficulty,
            "duration": self.duration,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "assigned_staff_id": self.assigned_staff_id,
            "assigned_staff_name": self.assigned_staff.username if self.assigned_staff else "Unassigned",
            "status": self.status,
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else "",
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else ""
        }


class Booking(db.Model):
    __tablename__ = "booking"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="Booked")  # 'Booked', 'Cancelled', 'Completed'

    user = db.relationship("User", backref="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "Unknown",
            "trek_id": self.trek_id,
            "trek_name": self.trek.trek_name if self.trek else "Unknown",
            "trek_location": self.trek.location if self.trek else "Unknown",
            "trek_difficulty": self.trek.difficulty if self.trek else "Unknown",
            "trek_start_date": self.trek.start_date.strftime("%Y-%m-%d") if (self.trek and self.trek.start_date) else "",
            "trek_end_date": self.trek.end_date.strftime("%Y-%m-%d") if (self.trek and self.trek.end_date) else "",
            "trek_status": self.trek.status if self.trek else "Unknown",
            "booking_date": self.booking_date.strftime("%Y-%m-%d") if self.booking_date else "",
            "status": self.status
        }
