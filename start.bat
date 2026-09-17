@echo off
chcp 65001 >nul
title Ownership Log - Launcher
color 0A

cd /d "%~dp0"

echo ========================================
echo   📊 Ownership Log - Launcher
echo ========================================
echo.
echo   در حال باز کردن دو پنجره...
echo.
echo   ① پنجره Streamlit (برنامه)
echo   ② پنجره Push (GitHub)
echo.
echo ========================================
echo.

REM چک کردن Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git نصب نیست!
    pause
    exit
)

REM ============================================================
REM پنجره ۱: Streamlit
REM ============================================================
start "📊 Ownership Log - Streamlit" cmd /k "cd /d "%~dp0" && color 0B && echo ======================================== && echo   🚀 Streamlit در حال اجرا... && echo ======================================== && echo. && echo   📱 لینک: http://localhost:8501 && echo. && echo   ⚠️  برای بستن: Ctrl+C && echo. && echo ======================================== && echo. && start http://localhost:8501 && streamlit run app.py"

REM کمی صبر کن تا پنجره اول باز شود
timeout /t 3 >nul

REM ============================================================
REM پنجره ۲: Push به GitHub
REM ============================================================
start "📤 Push to GitHub" cmd /k "cd /d "%~dp0" && color 0E && call "%~dp0push_menu.bat""

echo.
echo ✅ دو پنجره باز شد!
echo.
echo   ① Streamlit → در حال اجرا
echo   ② Push → آماده برای آپلود
echo.
echo این پنجره بسته می‌شود...
timeout /t 3 >nul
exit