# 🎨 Two-Panel Drawing Guide

## ✅ Updated Features

Your LED Matrix Drawer now supports **drawing on both 64x64 panels simultaneously**!

### What's New:

✓ **128x64 canvas** - Full two-panel display  
✓ **Visual panel separator** - Dashed line between panels  
✓ **Panel indicators** - Shows which panel you're drawing on  
✓ **Coordinate tracking** - Displays both panel-specific and absolute coordinates  
✓ **Full matrix support** - Both panels update via GPIO

---

## 🖼️ Canvas Layout

```
┌─────────────────────────────────────┐
│  Drawing Canvas - Two 64x64 Panels  │
├──────────────┬──────────────────────┤
│              │                      │
│   Panel 1    ┊    Panel 2          │
│   (64x64)    ┊    (64x64)          │
│   Cols 0-63  ┊    Cols 64-127      │
│              ┊                      │
│              ┊                      │
└──────────────┴──────────────────────┘
  ◄ Panel 1 ►    ◄ Panel 2 ►
```

The dashed vertical line separates the two panels.

---

## 🎮 How to Use

### 1. **Start the Application**
```bash
sudo python3 led_matrix_drawer.py
```

### 2. **Draw Across Both Panels**
- Click and drag anywhere on the 128x64 canvas
- Draw seamlessly across both panels
- The status bar shows which panel you're on

### 3. **Load to LED Panels**
Click **"Load to Panels"** to display your design on both physical LED panels via GPIO

---

## 📊 Coordinate System

### Status Bar Display:
```
Drawing at Panel 1: (32, 15) | Total: (32, 15)
                ↑       ↑              ↑
             Panel    Panel          Absolute
             Number   Position       Position
```

When drawing on Panel 2:
```
Drawing at Panel 2: (20, 30) | Total: (84, 30)
                ↑       ↑              ↑
             Panel 2  Position       (64 + 20 = 84)
                      on Panel 2
```

---

## 🛠️ Features

### Drawing Tools
- **Color Picker**: Choose any color
- **Quick Colors**: 8 preset colors
- **Clear Canvas**: Erases both panels
- **Fill Canvas**: Fills both panels with current color

### LED Matrix Control
- **Enable Matrix**: Real-time drawing on LED panels
- **Load to Panels**: Push complete design to both panels
- **Disable Matrix**: Turn off LED display

### Save/Load
- **Save Design**: Saves both panels (128x64 data)
- **Load Design**: Loads saved two-panel designs
- **Export PNG**: Exports 128x64 image

---

## 💾 File Format

Saved JSON files now include:
```json
{
    "width": 128,
    "height": 64,
    "panels": 2,
    "pixels": [...]
}
```

---

## 🎨 Drawing Tips

### 1. **Test Pattern**
Draw a vertical line down the middle to see the panel separation clearly.

### 2. **Panel-Spanning Art**
Create designs that flow across both panels for a seamless 128x64 display.

### 3. **Color Gradients**
Use different colors on each panel for easy identification.

### 4. **Real-Time vs Load**
- **Enable Matrix**: Best for live drawing
- **Load to Panels**: Best for complete designs

---

## 🔧 Technical Details

### Canvas Configuration
```python
panel_width = 64      # Width of each panel
panel_height = 64     # Height of each panel
total_width = 128     # Combined width
total_height = 64     # Total height
pixel_size = 6        # GUI pixel size (smaller to fit both panels)
```

### LED Matrix Configuration
```python
rows = 64             # 64 rows per panel
cols = 64             # 64 columns per panel
chain_length = 2      # Two panels chained
parallel = 1          # Single chain
```

### Display Mapping
```
GPIO → Controller → Panel 1 [0-63] → Panel 2 [64-127]
```

---

## 🎯 Quick Test

1. Run: `sudo python3 led_matrix_drawer.py`
2. Select a bright color (e.g., red)
3. Draw in the left half (Panel 1)
4. Select a different color (e.g., blue)
5. Draw in the right half (Panel 2)
6. Click **"Load to Panels"**
7. Both panels should light up with your design!

---

## 📈 Resolution Comparison

| Configuration | Canvas Size | Physical Display |
|---------------|-------------|------------------|
| **Before** | 64x64 | First panel only |
| **Now** | 128x64 | Both panels! |

---

## 🚀 Run Commands

```bash
# Standard run (with hardware)
sudo python3 led_matrix_drawer.py

# Or use the start script
./start.sh

# Test without hardware
python3 led_matrix_drawer.py
```

---

**Enjoy drawing on both panels! 🎨✨**

Your designs now span the full 128x64 display area!
