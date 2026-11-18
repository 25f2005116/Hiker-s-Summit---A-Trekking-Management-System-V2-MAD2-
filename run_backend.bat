@echo off
echo ========================================================
echo  Starting Hiker's Summit V2 - Flask Backend API Server
echo ========================================================
cd backend
call venv\Scripts\activate.bat
python app.py
pause
