@echo off
echo Starting Leads Scraper...

start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
start "Backend" cmd /k "cd /d %~dp0 && python run.py"

echo.
echo Launched in separate windows.
echo   API:       http://localhost:8000/api
echo   Dashboard: http://localhost:5173
echo   API Docs:  http://localhost:8000/docs
