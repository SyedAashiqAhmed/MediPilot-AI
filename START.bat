@echo off
echo ========================================
echo   MedCore AI - Starting Server
echo ========================================
echo.
echo Stopping any running Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Starting MedCore AI Server (app.py)...
echo.
python app.py
