import time
import sys
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

def test_image():
    print("Initializing Matrix...")
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.hardware_mapping = 'regular'
    options.gpio_slowdown = 4
    options.brightness = 50
    options.disable_hardware_pulsing = True
    
    try:
        matrix = RGBMatrix(options=options)
        print("Matrix Initialized.")
    except Exception as e:
        print(f"Failed to init matrix: {e}")
        return

    # Create a simple image
    print("Creating test image...")
    img = Image.new('RGB', (128, 64), (255, 0, 0)) # Red
    
    print("Creating offscreen canvas...")
    offscreen = matrix.CreateFrameCanvas()
    
    print("Setting pixels manually...")
    try:
        width, height = img.size
        pixels = img.load()
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                offscreen.SetPixel(x, y, r, g, b)
        print("Pixels set successfully.")
    except Exception as e:
        print(f"Error setting pixels: {e}")
        return

    print("Swapping canvas...")
    try:
        offscreen = matrix.SwapOnVSync(offscreen)
        print("Canvas swapped successfully.")
        time.sleep(2)
    except Exception as e:
        print(f"Error swapping canvas: {e}")

    print("Test complete.")

if __name__ == "__main__":
    test_image()
