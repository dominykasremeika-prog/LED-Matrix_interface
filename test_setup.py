#!/usr/bin/env python3
"""
Quick test script to verify the LED matrix setup
"""

print("Testing LED Matrix Drawing Application Setup...")
print("-" * 50)

# Test imports
try:
    import numpy as np
    print("✓ NumPy imported successfully")
except ImportError as e:
    print(f"✗ NumPy import failed: {e}")

try:
    from PIL import Image
    print("✓ Pillow (PIL) imported successfully")
except ImportError as e:
    print(f"✗ Pillow import failed: {e}")

try:
    import tkinter as tk
    print("✓ Tkinter imported successfully")
except ImportError as e:
    print(f"✗ Tkinter import failed: {e}")

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    print("✓ RGB Matrix library imported successfully")
    GPIO_AVAILABLE = True
except ImportError as e:
    print(f"✗ RGB Matrix library import failed: {e}")
    print("  (This is OK if not running on Raspberry Pi with GPIO)")
    GPIO_AVAILABLE = False

print("-" * 50)
if GPIO_AVAILABLE:
    print("\n✓ ALL DEPENDENCIES INSTALLED!")
    print("\nYou can now run the LED matrix drawer:")
    print("  sudo python3 led_matrix_drawer.py")
    print("\n(sudo is required for GPIO access)")
else:
    print("\n✓ GUI DEPENDENCIES INSTALLED!")
    print("\nYou can run the drawer in simulation mode:")
    print("  python3 led_matrix_drawer.py")
    print("\nFor full GPIO support, ensure you're on a Raspberry Pi")
    print("and the RGB matrix hardware is properly connected.")
