@echo off
title SmartBio Launcher
echo ========================================================
echo   Starting SmartBio Web Application...
echo ========================================================
echo.

:: Launch browser directly to the running application
start http://localhost:8000/

echo SmartBio is running at:
echo   - Web Application: http://localhost:8000
echo   - Vite Dev Server: http://localhost:5173
echo   - API Documentation: http://localhost:8000/docs
echo.
echo If the server is not already running in background, starting it now...
backend\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
pause
