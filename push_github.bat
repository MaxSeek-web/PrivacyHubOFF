@echo off
cd /d "C:\Claude\PrivacyHubApp"
echo =====================================
echo  Push PrivacyHub to GitHub Pages
echo =====================================
echo.
echo Enter your GitHub Personal Access Token:
echo (Settings - Developer settings - Personal access tokens - Tokens (classic))
echo.
set /p TOKEN=Token:
if "%TOKEN%"=="" (
  echo Token is empty! Exiting.
  pause
  exit /b 1
)
echo.
echo Pushing...
"C:\Users\maxim\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe" push "https://%TOKEN%@github.com/MaxSeek-web/PrivacyHubOFF.git" main
if %ERRORLEVEL%==0 (
  echo.
  echo ✅ SUCCESS! Site updated at:
  echo https://maxseek-web.github.io/PrivacyHubOFF/
) else (
  echo.
  echo ❌ ERROR! Check token and internet.
)
pause
