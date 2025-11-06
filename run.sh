#!/bin/bash
# Safe launcher for LED Matrix Drawer with proper permissions

echo "🚀 Starting LED Matrix Drawer..."

# Allow root to access X11 display
echo "📺 Setting up X11 permissions..."
xhost +local:root > /dev/null 2>&1

# Fix directory permissions for sudo access
echo "🔑 Checking directory permissions..."
chmod 755 ~ ~/Desktop ~/Desktop/Lemona 2>/dev/null || true
chmod 644 ~/Desktop/Lemona/*.{png,jpg,jpeg,gif,bmp} 2>/dev/null || true

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if hardware mode is needed
if [ "$1" == "--no-hardware" ] || [ "$1" == "-s" ]; then
    echo "🖥️  Running in simulation mode (no sudo needed)..."
    python3 led_matrix_drawer.py
else
    echo "🔌 Running with hardware support (sudo required)..."
    echo "💡 Tip: Use './run.sh --no-hardware' for simulation mode"
    echo ""
    # Run with sudo, preserving environment variables
    sudo -E python3 led_matrix_drawer.py
fi

# Clean up X11 permissions
echo ""
echo "🧹 Cleaning up..."
xhost -local:root > /dev/null 2>&1

echo "✅ Done!"
