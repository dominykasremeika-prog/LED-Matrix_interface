#!/bin/bash

# Installation script for RGB LED Matrix library on Raspberry Pi
# This script will install the necessary dependencies and compile the library

echo "=========================================="
echo "RGB LED Matrix Library Installation"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi."
    echo "The RGB Matrix library requires a Raspberry Pi with GPIO pins."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install required system packages
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pillow \
    python3-tk \
    git \
    build-essential \
    libgraphicsmagick++-dev \
    libwebp-dev

# Clone the RGB Matrix library
echo "Cloning RGB Matrix library..."
cd ~/
if [ -d "rpi-rgb-led-matrix" ]; then
    echo "Directory already exists. Pulling latest changes..."
    cd rpi-rgb-led-matrix
    git pull
else
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
    cd rpi-rgb-led-matrix
fi

# Build the library
echo "Building RGB Matrix library..."
make build-python PYTHON=$(which python3)

# Install the Python bindings
echo "Installing Python bindings..."
sudo make install-python PYTHON=$(which python3)

# Install additional Python requirements
echo "Installing Python packages..."
pip3 install --user numpy Pillow

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "You can now run the LED Matrix drawer with:"
echo "  python3 led_matrix_drawer.py"
echo ""
echo "Note: You may need to run with sudo for GPIO access:"
echo "  sudo python3 led_matrix_drawer.py"
echo ""
