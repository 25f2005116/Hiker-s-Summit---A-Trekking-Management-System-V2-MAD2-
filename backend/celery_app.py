from celery import Celery
from celery.schedules import crontab
from config import Config

def make_celery(app_name=__name__):
    celery_instance = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=[
            "tasks.reminders",
            "tasks.reports",
            "tasks.exports"
        ]
    )
    celery_instance.conf.update(
        timezone="Asia/Kolkata",
        enable_utc=False,
        beat_schedule={
            "send-daily-trek-reminders": {
                "task": "tasks.reminders.send_daily_reminders",
                # Run daily at 08:00 AM
                "schedule": crontab(hour=8, minute=0),
            },
            "generate-monthly-activity-report": {
                "task": "tasks.reports.send_monthly_report_task",
                # Run on the 1st of every month at midnight
                "schedule": crontab(day_of_month=1, hour=0, minute=0),
            }
        }
    )
    return celery_instance

celery = make_celery()
