@echo off
echo ========================================
echo   CollabSpace Backend Setup
echo ========================================
echo.

cd backend

echo [1/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Setup complete!
echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo 1. Download Firebase Admin SDK credentials
echo 2. Save as: backend\firebase-credentials.json
echo 3. Update databaseURL in backend\app.py
echo 4. Run: python app.py
echo.
echo Press any key to exit...
pause > nul
