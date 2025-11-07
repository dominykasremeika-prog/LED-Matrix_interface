#!/bin/bash
# Installation script for Raspberry Pi LED Matrix Controller

echo "========================================"
echo "LED Matrix Controller - Setup"
echo "========================================"

# Update system
echo "Updating system packages..."
sudo apt-get update

# Install Python and pip
echo "Installing Python dependencies..."
sudo apt-get install -y python3-dev python3-pip

# Install system dependencies for rpi-rgb-led-matrix
echo "Installing build dependencies..."
sudo apt-get install -y build-essential git

# Clone and install rpi-rgb-led-matrix library
echo "Installing rpi-rgb-led-matrix library..."
if [ ! -d "rpi-rgb-led-matrix" ]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
fi

cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
cd ..

# Install Python packages
echo "Installing Python packages..."
pip3 install requests

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit rpi_led_controller.py and set your server IP:"
echo "   API_URL = 'http://YOUR_SERVER_IP:8000/api/display'"
echo ""
echo "2. Test the controller:"
echo "   sudo python3 rpi_led_controller.py"
echo ""
echo "3. To run automatically on boot, see README_RPI.md"
echo ""
