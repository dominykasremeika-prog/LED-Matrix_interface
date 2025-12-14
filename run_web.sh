#!/bin/bash
# Launcher for LED Matrix Web Interface

echo "🌐 Starting LED Matrix Web Interface..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if hardware mode is needed
if [ "$1" == "--no-hardware" ] || [ "$1" == "-s" ]; then
    echo "🖥️  Running in simulation mode (no sudo needed)..."
    python3 web_app.py --no-hardware
else
    echo "🔌 Running with hardware support (sudo required)..."
    echo "💡 Tip: Use './run_web.sh --no-hardware' for simulation mode"
    echo ""
    # Run with sudo
    sudo python3 web_app.py
fi
