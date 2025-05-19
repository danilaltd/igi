@echo off
setlocal enabledelayedexpansion

echo Checking environment...

echo Creating logs directory if not exists...
if not exist logs mkdir logs

echo Clearing logs...
if exist logs\*.log del /Q logs\*.log

echo Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo Checking Django installation...
python -c "import django" > nul 2>&1
if errorlevel 1 (
    echo Error: Django is not installed
    exit /b 1
)

echo Checking required files...
if not exist manage.py (
    echo Error: manage.py not found
    exit /b 1
)
if not exist reset_db.py (
    echo Error: reset_db.py not found
    exit /b 1
)
if not exist load_data.py (
    echo Error: load_data.py not found
    exit /b 1
)

echo Checking fixtures directory...
if not exist myparking\fixtures (
    echo Error: fixtures directory not found
    exit /b 1
)

echo Resetting database...
python reset_db.py
if errorlevel 1 (
    echo Error: Failed to reset database
    exit /b 1
)

echo Running migrations...
python manage.py makemigrations --no-input
if errorlevel 1 (
    echo Error: Failed to create migrations
    exit /b 1
)

python manage.py migrate --no-input
if errorlevel 1 (
    echo Error: Failed to apply migrations
    exit /b 1
)

echo Loading test data...
python load_data.py
if errorlevel 1 (
    echo Error: Failed to load test data
    exit /b 1
)

echo Starting server...
python manage.py runserver