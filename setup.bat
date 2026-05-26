@echo off
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Local 'python' command failed. Attempting absolute path...
    "C:\Users\HP 240\AppData\Local\Programs\Python\Python311\python.exe" -m venv venv
)

if exist venv\Scripts\pip.exe (
    echo Virtual environment created successfully.
    echo Installing requirements from requirements.txt...
    "venv\Scripts\pip.exe" install -r requirements.txt
    echo All requirements installed successfully!
) else (
    echo Failed to create virtual environment. Make sure Python is installed and in your PATH.
    exit /b 1
)
