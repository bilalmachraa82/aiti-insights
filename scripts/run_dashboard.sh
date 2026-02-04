#!/bin/bash
# Run AITI Insights Dashboard

set -e

cd "$(dirname "$0")/.."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Starting AITI Insights Dashboard..."
echo "Open http://localhost:8501 in your browser"
echo ""

streamlit run src/aiti_insights/dashboard.py
