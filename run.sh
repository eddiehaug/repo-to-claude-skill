#!/bin/bash

# Repo-to-Skill Converter - Run Script

echo "🤖 Repo-to-Skill Converter"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found"
    echo "Please create .env file with your Claude API key:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your API key"
    echo ""
fi

# Run Streamlit app
echo ""
echo "Starting Streamlit app..."
echo "Open your browser to: http://localhost:8501"
echo ""

streamlit run app.py
