#!/bin/bash

echo "Setting up Market Data Service..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements/base.txt

# Start infrastructure services
docker-compose up -d postgres kafka zookeeper redis

# Wait for services
echo "Waiting for services to start..."
sleep 15

echo "Setup complete!"
echo "Starting Market Data Service..."
echo ""
echo "Available endpoints:"
echo "• Health: http://localhost:8000/health"
echo "• API Docs: http://localhost:8000/docs"
echo "• Price: http://localhost:8000/prices/latest?symbol=AAPL"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the application
python -m app.main