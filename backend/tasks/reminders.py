import os
import json
import urllib.request
from datetime import date, timedelta
from config import Config
from celery_app import celery
from database import db
from models import Trek, Booking, User
from tasks.reports import send_email_notification

def process_daily_reminders():
    """Scans for treks starting tomorrow and sends reminders to participants."""
    tomorrow = date.today() + timedelta(days=1)
    upcoming_treks = Trek.query.filter(Trek.start_date == tomorrow, Trek.status == "Open").all()

    reminders_sent = []
    webhook_url = os.environ.get("WEBHOOK_URL", Config.WEBHOOK_URL)

    for trek in upcoming_treks:
        bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
        for b in bookings:
            user = b.user
            message = (
                f"Reminder for {user.username}: Your trek '{trek.trek_name}' at {trek.location} "
                f"starts tomorrow ({trek.start_date})! Duration: {trek.duration} days. "
                f"Please carry valid ID, proper hiking shoes, and water."
            )
            print(f"[Daily Reminder] To: {user.username} ({user.contact_details}) -> {message}")

            # 1. Send via Webhook (Google Chat / Discord / Slack if configured)
            if webhook_url:
                try:
                    payload = json.dumps({"text": message}).encode("utf-8")
                    req = urllib.request.Request(
                        webhook_url,
                        data=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=5) as response:
                        print(f"[Webhook Dispatch] Successfully sent to webhook for {user.username} (HTTP {response.status})")
                except Exception as e:
                    print(f"[Webhook Dispatch] Failed ({e})")

            # 2. Send via Email (SMTP or simulated delivery)
            user_email = user.contact_details if (user.contact_details and "@" in user.contact_details) else f"{user.username}@gmail.com"
            send_email_notification(
                to_email=user_email,
                subject=f"Upcoming Trek Reminder: {trek.trek_name} Starts Tomorrow!",
                html_content=f"<h3>{trek.trek_name} - Trek Starting Tomorrow</h3><p>{message}</p>"
            )

            reminders_sent.append({
                "user": user.username,
                "contact": user.contact_details,
                "trek": trek.trek_name,
                "date": str(trek.start_date)
            })

    return reminders_sent


@celery.task(name="tasks.reminders.send_daily_reminders")
def send_daily_reminders():
    from app import app
    with app.app_context():
        results = process_daily_reminders()
        return f"Processed {len(results)} reminders"
