@echo off
chcp 65001 >nul
echo ==========================================
echo   🛑 Stopping PrivacyHub Server...
echo ==========================================
echo.

set "PID_FILE=C:\Claude\PrivacyHubApp\server.pid"

if exist "%PID_FILE%" (
    for /f %%i in (%PID_FILE%) do (
        echo 🔍 Found server PID: %%i
        taskkill /PID %%i /F > nul 2>&1
        if %ERRORLEVEL%==0 (
            echo ✅ Server stopped successfully!
        ) else (
            echo ⚠️  Could not stop server. It may have already exited.
        )
    )
    del "%PID_FILE%" > nul 2>&1
) else (
    echo 🔍 PID file not found. Trying to find python server...
    tasklist | findstr "python" > nul
    if %ERRORLEVEL%==0 (
        echo ⚠️  Python processes found.
        echo    Please stop them manually via Task Manager,
        echo    or restart your computer.
    ) else (
        echo ℹ️  No running PrivacyHub server found.
    )
)

echo.
echo ==========================================
pause
