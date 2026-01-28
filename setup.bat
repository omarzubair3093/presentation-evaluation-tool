@echo off
REM Presentation Evaluation Tool - Windows Setup Script

echo.
echo ========================================
echo Presentation Evaluation Tool - Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo Please install Python 3.11 from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Get your Anthropic API key from: https://console.anthropic.com/
echo 2. Run: set ANTHROPIC_API_KEY=your-key-here
echo 3. Run: set SECRET_KEY=any-random-string
echo 4. Run: python app.py
echo 5. Open: http://localhost:5000
echo.
echo Or use the quick start command:
echo set ANTHROPIC_API_KEY=your-key ^&^& set SECRET_KEY=random ^&^& python app.py
echo.
echo For deployment to Render.com, see DEPLOYMENT_GUIDE.md
echo.
pause
