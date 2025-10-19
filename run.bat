@echo off
REM Repo-to-Skill Converter - Run Script (Windows)

echo 🤖 Repo-to-Skill Converter
echo ==========================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo.
    echo ⚠️  No .env file found
    echo Please create .env file with your Claude API key:
    echo   copy .env.example .env
    echo   # Then edit .env and add your API key
    echo.
)

REM Run Streamlit app
echo.
echo Starting Streamlit app...
echo Open your browser to: http://localhost:8501
echo.

streamlit run app.py
