@echo off
echo ========================================================
echo  Starting Hiker's Summit V2 - Celery Beat (Scheduler)
echo ========================================================
cd backend
call venv\Scripts\activate.bat
celery -A celery_app.celery beat --loglevel=info
pause
