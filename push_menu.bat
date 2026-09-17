@echo off
chcp 65001 >nul
title Push to GitHub
color 0E

cd /d "%~dp0"

:menu
cls
echo ========================================
echo   📤 Push to GitHub
echo ========================================
echo.
echo   1. 🚀 آپلود به GitHub (Push)
echo   2. 📊 وضعیت Git (Status)
echo   3. 📥 دریافت از GitHub (Pull)
echo   4. 🔗 باز کردن GitHub
echo   5. 🚪 بستن
echo.
echo ========================================
set /p choice="انتخاب (1-5): "

if "%choice%"=="1" goto push
if "%choice%"=="2" goto status
if "%choice%"=="3" goto pull
if "%choice%"=="4" goto open_github
if "%choice%"=="5" exit
goto menu

REM ============================================================
:push
cls
echo ========================================
echo   📤 آپلود به GitHub
echo ========================================
echo.

echo 📊 بررسی تغییرات...
git status --short
echo.

git add .
if errorlevel 1 (
    echo ❌ خطا در add
    pause
    goto menu
)

echo 💾 ذخیره...
git commit -m "Update: %date% %time%"

if errorlevel 1 (
    echo.
    echo ⚠️  هیچ تغییری نیست
    echo.
    timeout /t 2 >nul
    goto menu
)

echo.
echo 🚀 در حال آپلود به GitHub...
git push

if errorlevel 1 (
    echo.
    echo ❌ خطا در push!
    echo    Token را چک کن
    echo.
    pause
    goto menu
)

echo.
echo ========================================
echo   ✅ با موفقیت آپلود شد!
echo ========================================
echo.
echo   ⏱️  Streamlit Cloud → ۱۰-۳۰ ثانیه → آپدیت
echo.
timeout /t 3 >nul
goto menu

REM ============================================================
:status
cls
echo ========================================
echo   📊 وضعیت Git
echo ========================================
echo.
echo 📁 پوشه: %CD%
echo.
echo 📊 تغییرات:
git status
echo.
echo 📜 آخرین Commit:
git log -1 --oneline 2>nul
echo.
echo 🔗 Remote:
git remote -v
echo.
pause
goto menu

REM ============================================================
:pull
cls
echo ========================================
echo   📥 دریافت از GitHub
echo ========================================
echo.
git pull
echo.
pause
goto menu

REM ============================================================
:open_github
start https://github.com/12mobin/ownership-log
goto menu