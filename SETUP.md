# 🚀 Lemona - LED Matrix Drawer Setup Guide

Complete installation and setup instructions for the LED Matrix Drawing Application.

---

## 📋 Table of Contents
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Hardware Setup](#hardware-setup)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Software Requirements
- **Operating System:** Raspberry Pi OS (Raspbian) or any Debian-based Linux
- **Python:** 3.7 or higher
- **RAM:** 512MB minimum (1GB+ recommended)
- **Storage:** 500MB free space

### Hardware Requirements (Optional)
- **Raspberry Pi:** Any model with GPIO pins (Pi 3, 4, or Zero recommended)
- **LED Matrix Panels:** 2x 64x64 RGB LED panels (HUB75 interface)
- **Power Supply:** 5V 10A+ for LED panels
- **GPIO Adapter:** Adafruit RGB Matrix HAT or compatible

**Note:** The application can run in simulation mode without hardware!

---

## ⚡ Quick Start

For experienced users, here's the fast track:

```bash
# 1. Clone or download the project
cd ~/Desktop
# (If you have it already, skip to step 2)

# 2. Navigate to the project
cd Lemona

# 3. Install Python dependencies
pip3 install -r requirements.txt

# 4. (Optional) Install RGB Matrix library for hardware
./install_matrix_library.sh

# 5. Fix permissions
./fix-permissions.sh

# 6. Run the application
./run.sh
```

---

## 📦 Detailed Installation

### Step 1: System Update

Update your system first:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install System Dependencies

```bash
# Install Python and required system packages
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-tk \
    git \
    build-essential

# Verify Python version (should be 3.7+)
python3 --version
```

### Step 3: Install Python Packages

Navigate to the project directory and install requirements:

```bash
cd ~/Desktop/Lemona

# Install Python dependencies
pip3 install -r requirements.txt

# Or install manually:
pip3 install numpy pillow
```

### Step 4: Install RGB Matrix Library (For Hardware)

**Option A: Use the install script (Recommended)**

```bash
./install_matrix_library.sh
```

**Option B: Manual installation**

```bash
# Install dependencies
sudo apt-get install -y \
    python3-dev \
    python3-pillow \
    libgraphicsmagick++-dev \
    libwebp-dev

# Clone the RGB Matrix library
cd ~/
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix

# Build the library
make build-python PYTHON=$(which python3)

# Install the library
sudo make install-python PYTHON=$(which python3)

# Return to project directory
cd ~/Desktop/Lemona
```

### Step 5: Fix Permissions

```bash
# Fix directory and file permissions for sudo access
./fix-permissions.sh
```

This ensures the application can access files when running with sudo (required for GPIO access).

---

## 🔌 Hardware Setup

### LED Panel Wiring

If you have LED matrix hardware:

#### Connection Diagram

```
Raspberry Pi GPIO → RGB Matrix HAT → Panel 1 (64x64) → Panel 2 (64x64)
                         ↓
                    Power Supply (5V 10A+)
```

#### Panel Configuration

- **Panel 1:** Left panel (coordinates 0-63, 0-63)
- **Panel 2:** Right panel (coordinates 64-127, 0-63)
- **Chain Length:** 2 panels
- **Resolution:** 128x64 total (2x 64x64 panels)

#### Wiring Steps

1. **Connect RGB Matrix HAT to Raspberry Pi GPIO**
2. **Connect Panel 1 input to HAT output**
3. **Connect Panel 2 input to Panel 1 output**
4. **Connect power supply to both panels**
5. **DO NOT power panels from Raspberry Pi!**

For detailed wiring, see: `TWO_PANEL_GUIDE.md`

### Without Hardware (Simulation Mode)

No hardware? No problem! The application runs in simulation mode automatically:

```bash
# Run without sudo (simulation mode)
python3 led_matrix_drawer.py
```

---

## 🎮 Running the Application

### With LED Hardware

```bash
# Use the run script (recommended)
./run.sh

# Or manually with sudo
sudo -E python3 led_matrix_drawer.py
```

### Without LED Hardware (Simulation)

```bash
# Run without sudo
./run.sh --no-hardware

# Or directly
python3 led_matrix_drawer.py
```

### Using the Start Script

```bash
# Interactive start script
./start.sh
```

This will ask if you have hardware and run appropriately.

---

## 🎨 Features

### Drawing Tools
- **Freehand Drawing:** Click and drag to draw
- **Color Picker:** Choose any color
- **Quick Colors:** 8 preset colors
- **Fill Tool:** Fill entire canvas
- **Clear Tool:** Clear canvas

### Undo/Redo
- **Undo:** Ctrl+Z or click "⟲ Undo" button
- **Redo:** Ctrl+Y or Ctrl+Shift+Z or click "⟳ Redo" button
- **History:** Up to 50 undo levels

### File Operations
- **Save Design:** Export as JSON
- **Load Design:** Import JSON designs
- **Load Image:** Import PNG/JPG/GIF/BMP images
- **Export PNG:** Save canvas as image

### LED Matrix Control
- **Enable/Disable Matrix:** Toggle real-time updates
- **Load to Panels:** Push design to LED display
- **Real-time Updates:** See changes instantly on hardware

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo last action |
| Ctrl+Y | Redo last undone action |
| Ctrl+Shift+Z | Redo (alternative) |

---

## 🔧 Configuration

### Matrix Settings

Edit `led_matrix_drawer.py` to configure your panels:

```python
# In initialize_matrix() method
options.rows = 64              # Rows per panel
options.cols = 64              # Columns per panel
options.chain_length = 2       # Number of panels
options.brightness = 50        # Brightness (0-100)
options.gpio_slowdown = 4      # Reduce flickering (1-4)
```

### Drawing Performance

Adjust polling rate in `__init__` method:

```python
self.draw_throttle = 0.016  # 60fps (lower = faster but more CPU)
```

Recommended values:
- **0.016** = 60fps (smooth, recommended)
- **0.033** = 30fps (lower CPU usage)
- **0.008** = 120fps (very smooth, high CPU)

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Permission Denied on Image Upload

**Solution:**
```bash
./fix-permissions.sh
```

#### 2. Matrix Library Not Found

**Error:** `ImportError: No module named 'rgbmatrix'`

**Solution:**
```bash
# Run the install script
./install_matrix_library.sh

# Or install manually (see Step 4 above)
```

#### 3. GUI Won't Open with Sudo

**Solution:**
```bash
# Allow X11 access
xhost +local:root

# Run with environment preservation
sudo -E python3 led_matrix_drawer.py
```

Or just use:
```bash
./run.sh
```

#### 4. Panels Show Wrong Colors/Flicker

**Solution:**
Adjust `gpio_slowdown` in code (line ~171):

```python
options.gpio_slowdown = 4  # Try values 1-4
```

#### 5. Application Freezes

**Cause:** Drawing too fast

**Solution:**
Increase throttle value:
```python
self.draw_throttle = 0.033  # Reduce from 0.016
```

#### 6. Can't Access /home/tranas123

**Solution:**
```bash
chmod 755 ~
chmod 755 ~/Desktop
chmod 755 ~/Desktop/Lemona
```

### Testing

Run comprehensive tests:

```bash
# Test everything
./test-everything.sh

# Test image loading
python3 test_image_load.py

# Test with sudo
sudo python3 test_image_load.py
```

---

## 📁 Project Structure

```
Lemona/
├── led_matrix_drawer.py       # Main application
├── requirements.txt           # Python dependencies
├── SETUP.md                   # This file
├── README.md                  # Project overview
├── run.sh                     # Easy launcher script
├── start.sh                   # Interactive startup
├── fix-permissions.sh         # Permission fix tool
├── install_matrix_library.sh  # Matrix library installer
├── test_image_load.py         # Image loading test
├── test-everything.sh         # Comprehensive test
├── test_image.png             # Sample test image
└── docs/
    ├── IMAGE_UPLOAD_GUIDE.md
    ├── TWO_PANEL_GUIDE.md
    ├── TROUBLESHOOTING_IMAGE_UPLOAD.md
    └── PERMISSIONS_FIXED.md
```

---

## 🔄 Updating the Application

```bash
# Pull latest changes (if using git)
cd ~/Desktop/Lemona
git pull

# Reinstall dependencies if requirements changed
pip3 install -r requirements.txt

# Fix permissions after update
./fix-permissions.sh
```

---

## 🆘 Getting Help

### Check Documentation
- `README.md` - Project overview
- `IMAGE_UPLOAD_GUIDE.md` - How to load images
- `TWO_PANEL_GUIDE.md` - Hardware setup
- `TROUBLESHOOTING_IMAGE_UPLOAD.md` - Image issues

### Run Tests
```bash
./test-everything.sh
```

### Verify Setup
```bash
# Check Python
python3 --version

# Check dependencies
pip3 list | grep -E "numpy|Pillow"

# Check permissions
ls -ld ~ ~/Desktop ~/Desktop/Lemona

# Check matrix library
python3 -c "from rgbmatrix import RGBMatrix; print('✓ Matrix library installed')"
```

---

## 🎯 Next Steps

1. **Run the application:**
   ```bash
   ./run.sh
   ```

2. **Try the test image:**
   - Click "Load Image"
   - Select `test_image.png`
   - Click "Load to Panels" (if you have hardware)

3. **Draw something:**
   - Choose a color
   - Click and drag on canvas
   - Try Ctrl+Z to undo!

4. **Save your work:**
   - Click "Save Design" (JSON format)
   - Click "Export PNG" (image format)

---

## ✅ Installation Complete!

You're all set! Enjoy creating LED matrix art! 🎨✨

For questions or issues, check the troubleshooting section above or review the documentation files.

---

**Last Updated:** November 6, 2025
**Version:** 2.0
**Python:** 3.7+
**Platform:** Raspberry Pi / Linux
