@echo off
cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Python OK
python --version

echo [2/3] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo [3/3] Installing packages...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
venv\Scripts\pip install -r requirements.txt

echo.
echo Setup complete! Run start.bat to launch.
pause
