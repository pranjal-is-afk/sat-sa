@echo off
setlocal EnableDelayedExpansion

echo.
echo  ================================
echo   SAT-SA Setup Script v1.0
echo   Supervisory Analytics Tool
echo  ================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Install Node.js 18+ from nodejs.org
    exit /b 1
)

echo [1/6] Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/6] Installing Python dependencies...
pip install --quiet -r backend\requirements.txt
if errorlevel 1 ( echo [ERROR] pip install failed & exit /b 1 )

echo [3/6] Installing Node.js dependencies...
cd frontend
call npm.cmd install --silent
if errorlevel 1 ( echo [ERROR] npm install failed & cd .. & exit /b 1 )

echo [4/6] Building React frontend...
call npm.cmd run build
if errorlevel 1 ( echo [ERROR] Frontend build failed & cd .. & exit /b 1 )
cd ..

echo [5/6] Initialising database...
python -c "import sys; sys.path.insert(0,'backend'); from db import engine; from models.orm import Base; Base.metadata.create_all(bind=engine); print('DB OK')"

echo [6/6] Generating synthetic sample data...
if not exist data\sample mkdir data\sample
python data\generate_sample_data.py

echo.
echo  ================================
echo   Setup complete!
echo  ================================
echo.
echo  To start: run start.bat
echo  Then open: http://localhost:8000
echo  Sample data: data\sample\
echo.
