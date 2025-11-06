# 🎨 Lemona - LED Matrix Drawing Application

A powerful GUI application to draw on RGB LED matrix displays using Raspberry Pi GPIO pins. Create pixel art, load images, and display them on your LED matrix panels in real-time!

## ✨ Features

- 🖌️ **Freehand Drawing** - Click and drag to draw pixel art
- 🎨 **Color Picker** - Choose from millions of colors
- 🔄 **Undo/Redo** - Full undo/redo support (Ctrl+Z / Ctrl+Y)
- 📷 **Image Import** - Load PNG, JPG, GIF, BMP images
- 💾 **Save/Load Designs** - Save your artwork as JSON
- 📤 **Export PNG** - Export your designs as images
- ⚡ **Real-time Updates** - See changes instantly on LED matrix
- 🎮 **Simulation Mode** - Works without hardware for testing
- ⌨️ **Keyboard Shortcuts** - Fast workflow with hotkeys
- 🔧 **Optimized Performance** - Smart throttling for smooth drawing

## 🖥️ System Requirements

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd ~/Desktop/Lemona

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Fix permissions
./fix-permissions.sh

# 4. Run the application
./run.sh
```

For detailed setup instructions, see **[SETUP.md](SETUP.md)**.

---

## 🔧 Hardware Setup
- Raspberry Pi (3B+, 4, or newer recommended)
- 2x 64x64 RGB LED Matrix panels
- RGB LED Matrix HAT/Bonnet or GPIO connection
- LED Matrix Controller
- Power supply (5V, 10A+ recommended for two 64x64 panels)

### Wiring Configuration
This application is configured for:
- **Resolution**: 64x64 pixels per panel (128x64 total)
- **Configuration**: 2x 64x64 panels chained together
- **Panel 1**: Connected to GPIO pins via LED matrix controller
- **Panel 2**: Chained from Panel 1's output port

The default configuration uses:
- 64 rows per panel
- 64 columns per panel
- 2 panels in chain (chain_length = 2)
- Single parallel chain

### GPIO Pins Used
The RGB Matrix typically uses these GPIO pins on Raspberry Pi:
- R1, G1, B1, R2, G2, B2 (color data)
- A, B, C, D (row select)
- CLK, LAT, OE (control signals)

Refer to your specific LED matrix HAT/adapter documentation for exact pin mappings.

## Software Installation

### Option 1: Automatic Installation (Recommended for Raspberry Pi)

Run the installation script:
```bash
chmod +x install_matrix_library.sh
./install_matrix_library.sh
```

### Option 2: Manual Installation

1. **Install system dependencies:**
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pillow python3-tk git build-essential
```

2. **Install RGB Matrix Library:**
```bash
cd ~/
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```

3. **Install Python requirements:**
```bash
pip3 install -r requirements.txt
```

## Running the Application

### With GPIO (on Raspberry Pi):
```bash
sudo python3 led_matrix_drawer.py
```
Note: `sudo` is required for GPIO access.

### Without GPIO (simulation mode):
```bash
python3 led_matrix_drawer.py
```
The application will run in simulation mode if the RGB matrix library is not available.

## 🎮 Usage

### Drawing Tools
1. **Select a color**: Use the color picker or quick color buttons
2. **Draw**: Click and drag on the canvas
3. **Undo**: Press Ctrl+Z or click the Undo button
4. **Redo**: Press Ctrl+Y or click the Redo button
5. **Clear**: Use "Clear Canvas" to erase everything
6. **Fill**: Use "Fill Canvas" to fill with the current color

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| **Ctrl+Z** | Undo last action |
| **Ctrl+Y** | Redo last undone action |
| **Ctrl+Shift+Z** | Redo (alternative) |

### Image Operations
- **Load Image**: Import PNG/JPG/GIF/BMP images (auto-resizes to 128x64)
- **Save Design**: Save your drawing as JSON
- **Load Design**: Load a previously saved design
- **Export PNG**: Export your design as an image file

### LED Matrix Control
1. Click **"Enable Matrix"** to enable real-time drawing on the physical LED panels
2. Draw on the canvas and it will update live on the panels
3. Click **"Load to Panels"** to push your entire design to the LED matrix at once
4. Click **"Disable Matrix"** to turn off the display

## Configuration

To modify the matrix configuration, edit the `initialize_matrix()` function in `led_matrix_drawer.py`:

```python
options = RGBMatrixOptions()
options.rows = 64              # Rows per panel (64 for your panels)
options.cols = 64              # Columns per panel (64 for your panels)
options.chain_length = 2       # Number of panels chained (2 panels)
options.parallel = 1           # Single chain
options.hardware_mapping = 'regular'  # or 'adafruit-hat', 'adafruit-hat-pwm'
options.gpio_slowdown = 4      # Adjust if flickering occurs (1-4)
options.brightness = 50        # Brightness (0-100)
```

### Common Configurations

**For single 64x64 panel:**
```python
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
```

**For 2x 64x64 panels chained (128x64 total - as configured):**
```python
options.rows = 64
options.cols = 64
options.chain_length = 2
options.parallel = 1
```

**For 32x32 display (single panel):**
```python
options.rows = 32
options.cols = 32
options.chain_length = 1
options.parallel = 1
```

**For 64x32 display (two panels chained):**
```python
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
```

**For 64x64 display (as configured):**
```python
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
```

**Note:** The current configuration displays on only the first 64x64 of the 128x64 total area. If you want to use both panels as a single 128x64 display, you'll need to adjust the canvas size in the code.

## Troubleshooting

### No display on LED matrix
- Check power supply (LEDs require significant current)
- Verify GPIO connections
- Try different `gpio_slowdown` values (1-4)
- Check `hardware_mapping` option matches your adapter

### Flickering display
- Increase `gpio_slowdown` value
- Reduce brightness
- Check power supply stability

### Permission errors
- Run with `sudo` for GPIO access
- Add user to gpio group: `sudo usermod -a -G gpio $USER`

### Import errors
- Ensure RGB matrix library is properly installed
- Check Python version compatibility (Python 3.6+)
- Verify all requirements are installed

## Performance Tips

1. **Brightness**: Lower brightness reduces power consumption and heat
2. **GPIO Slowdown**: Higher values reduce flickering but may decrease refresh rate
3. **Disable hardware pulsing**: Already set for better compatibility

## License

This project is provided as-is for educational and personal use.

## Credits

- Uses the excellent [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library by Henner Zeller
- Built with Python, Tkinter, NumPy, and Pillow

## Support

For issues with:
- **This application**: Check the code and configuration
- **RGB Matrix library**: Visit https://github.com/hzeller/rpi-rgb-led-matrix
- **Hardware setup**: Consult your LED matrix panel and adapter documentation
