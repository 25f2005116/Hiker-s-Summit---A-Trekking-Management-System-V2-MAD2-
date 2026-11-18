import os
import csv
from datetime import datetime
from config import Config
from database import db
from models import User, Booking, Trek
from celery_app import celery

@celery.task(name="tasks.exports.export_user_bookings_csv")
def export_user_bookings_csv(user_id):
    """User Triggered Async Job - Export Booking History as CSV."""
    from app import app
    with app.app_context():
        os.makedirs(Config.EXPORTS_FOLDER, exist_ok=True)
        
        user = User.query.get(user_id)
        username = user.username if user else f"user_{user_id}"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"booking_history_{username}_{timestamp}.csv"
        filepath = os.path.join(Config.EXPORTS_FOLDER, filename)

        bookings = Booking.query.filter_by(user_id=user_id).all()

        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "User ID",
                "Username",
                "Trek Name",
                "Location",
                "Difficulty",
                "Duration (in days)",
                "Start Date",
                "End Date",
                "Booking Date",
                "Status"
            ])
            for b in bookings:
                trek = b.trek
                writer.writerow([
                    b.user_id,
                    username,
                    trek.trek_name if trek else "N/A",
                    trek.location if trek else "N/A",
                    trek.difficulty if trek else "N/A",
                    trek.duration if trek else 0,
                    trek.start_date.strftime("%Y-%m-%d") if (trek and trek.start_date) else "",
                    trek.end_date.strftime("%Y-%m-%d") if (trek and trek.end_date) else "",
                    b.booking_date.strftime("%Y-%m-%d") if b.booking_date else "",
                    b.status
                ])

        return filename
