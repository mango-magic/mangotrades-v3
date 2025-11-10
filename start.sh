#!/bin/bash

# MangoTrades V3 Startup Script

echo "🥭 Starting MangoTrades V3..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Initialize database
echo "Initializing database..."
python3 -c "from database import init_db; init_db(); print('Database initialized!')"

# Start the Flask server
echo ""
echo "🚀 Starting Flask API server..."
echo "Dashboard: http://localhost:5000"
echo "API: http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py

