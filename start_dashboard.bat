@echo off
echo ========================================
echo Starting Threat Intelligence Dashboard
echo ========================================
echo.
echo Starting Backend (Flask API)...
start "Backend API" cmd /k "cd /d %~dp0dashboard\backend && python app.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting Frontend (React)...
start "Frontend" cmd /k "cd /d %~dp0dashboard\frontend && npm run dev"
echo.
echo ========================================
echo Dashboard should open in your browser:
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:5000
echo ========================================
echo.
echo Press any key to open the dashboard in browser...
pause >nul
start http://localhost:5173
