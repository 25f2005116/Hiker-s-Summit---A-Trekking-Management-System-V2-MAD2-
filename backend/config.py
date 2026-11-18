import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "trekking-mad2-super-secret-key-2026")
    
    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'trekking_v2.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Authentication
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-trekking-key-secure-2026-super-strong-secret-token")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Redis Configuration (Cache & Celery Broker)
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # Exports & Reports directories
    EXPORTS_FOLDER = os.path.join(BASE_DIR, "exports")
    REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
    
    # Webhook URL for Daily Reminders (Google Chat / Webhook.site)
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://webhook.site/3d757be2-b7fa-4517-864b-e454b4ce0143")
