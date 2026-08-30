@echo off
chcp 65001 >nul
title PrivacyHub Server
cd /d "C:\Claude\PrivacyHubApp"

:: Check if already running
if exist "server.pid" (
    echo ⚠️  Server might already be running!
    echo    If not, delete server.pid manually.
    pause
    exit /b
)

echo ==========================================
echo   🚀 Starting PrivacyHub Server...
echo ==========================================
echo.
echo 📝 Server will run at:
echo    http://127.0.0.1:8080
echo    http://privacyhub.local:8080
echo.
echo ⛔ Press Ctrl+C to STOP server
echo ==========================================
echo.

python server.py

:: When server stops
echo.
echo ==========================================
echo   ✅ Server stopped!
echo ==========================================
pause
