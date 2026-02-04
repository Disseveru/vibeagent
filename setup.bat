@echo off
echo 🚀 VibeAgent Setup Script
echo ==========================
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo ✓ Python found

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip > nul 2>&1
echo ✓ Pip upgraded

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

REM Create .env if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env file...
    copy .env.example .env
    echo ✓ .env file created - please edit it with your settings
) else (
    echo ✓ .env file already exists
)

echo.
echo ✅ Setup complete!
echo.
echo 📖 Next steps:
echo 1. Edit .env with your RPC URLs and wallet address
echo 2. Run the web interface: python -m vibeagent.cli web
echo    OR use CLI: python -m vibeagent.cli init-agent --help
echo.
echo 💡 For detailed instructions, see docs\USER_GUIDE.md
echo.
pause
