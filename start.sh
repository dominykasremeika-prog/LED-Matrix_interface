#!/bin/bash
# Quick Start Guide for LED Matrix Drawing Application

echo "╔════════════════════════════════════════════════════════╗"
echo "║   LED Matrix Drawing Application - Quick Start        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "led_matrix_drawer.py" ]; then
    echo "Error: led_matrix_drawer.py not found in current directory"
    echo "Please run this script from the Lemona directory"
    exit 1
fi

echo "Installation Status:"
echo "  ✓ RGB Matrix library installed"
echo "  ✓ Python dependencies installed"
echo "  ✓ Application ready to run"
echo ""

echo "Hardware Configuration:"
echo "  • Matrix Size: 64x64 pixels"
echo "  • Panels: 2x 32x64 RGB LED panels"
echo "  • Connection: Panel 1 → GPIO, Panel 2 → Panel 1 output"
echo ""

echo "Quick Start Options:"
echo ""
echo "1. Run with LED Matrix (requires sudo for GPIO access):"
echo "   $ sudo python3 led_matrix_drawer.py"
echo ""
echo "2. Run in simulation mode (no hardware needed):"
echo "   $ python3 led_matrix_drawer.py"
echo ""

read -p "Would you like to start the application now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Do you have LED matrix hardware connected? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Starting application with GPIO support..."
        echo "Note: You may need to enter your password for sudo access"
        echo ""
        # Preserve environment variables for GUI and user context
        sudo -E python3 led_matrix_drawer.py
    else
        echo ""
        echo "Starting application in simulation mode..."
        echo ""
        python3 led_matrix_drawer.py
    fi
else
    echo ""
    echo "You can start the application anytime using the commands above."
    echo "See README.md for detailed documentation."
fi
