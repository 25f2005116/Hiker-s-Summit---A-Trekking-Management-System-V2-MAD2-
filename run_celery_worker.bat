@echo off
echo ========================================================
echo  Starting Hiker's Summit V2 - Celery Worker
echo ========================================================
cd backend
call venv\Scripts\activate.bat
celery -A celery_app.celery worker --loglevel=info -P solo
pause
