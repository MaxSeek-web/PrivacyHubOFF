@echo off
chcp 65001 >nul
echo ==========================================
echo   PrivacyHub GitHub Push
echo ==========================================
echo.

:: Find git
echo 🔍 Looking for git...
set "GIT_EXE=C:\Users\maxim\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"

if exist "%GIT_EXE%" (
    echo ✅ Found git: %GIT_EXE%
) else (
    echo ❌ Git not found at expected path!
    echo Trying to find git in common locations...

    for %%G in (
        "C:\Program Files\Git\cmd\git.exe"
        "C:\Program Files (x86)\Git\cmd\git.exe"
        "C:\Users\maxim\AppData\Local\Programs\Git\cmd\git.exe"
    ) do (
        if exist "%%G" (
            set "GIT_EXE=%%G"
            echo ✅ Found git: %%G
            goto :found_git
        )
    )

    echo.
    echo ❌ ERROR: Git not found!
    echo Please enter full path to git.exe manually.
    set /p GIT_EXE="Path to git.exe: "
    if not exist "%GIT_EXE%" (
        echo ❌ File does not exist. Exiting.
        pause
        exit /b 1
    )
)

:found_git
echo.
echo 📂 Changing to repo directory...
cd /d "C:\Claude\PrivacyHubApp"

echo.
echo 📝 Enter your GitHub Personal Access Token:
echo (Get it at: github.com -^> Settings -^> Developer settings -^> Tokens -^> Generate new token)
echo.
set /p TOKEN="Token: "

if "%TOKEN%"=="" (
    echo ❌ Token cannot be empty!
    pause
    exit /b 1
)

echo.
echo 🚀 Pushing to GitHub...
echo.
"%GIT_EXE%" push "https://%TOKEN%@github.com/MaxSeek-web/PrivacyHubOFF.git" main --force

if %ERRORLEVEL%==0 (
    echo.
    echo ==========================================
    echo   ✅ SUCCESS! Site updated!
    echo ==========================================
    echo.
    echo 🌐 Your site will be live at:
    echo    https://1000k.ru
    echo    https://maxseek-web.github.io/PrivacyHubOFF/
    echo.
    echo ⏳ Wait 2-5 minutes for changes to appear.
) else (
    echo.
    echo ==========================================
    echo   ❌ PUSH FAILED!
    echo ==========================================
    echo.
    echo Possible reasons:
    echo - Wrong token
    echo - No internet
    echo - Repository access denied
    echo.
    echo Make sure your token has 'repo' scope!
)

pause
