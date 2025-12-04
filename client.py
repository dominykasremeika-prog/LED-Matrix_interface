import sys
import time
import json
import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Try to import rgbmatrix. If not available, print error.
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except ImportError:
    print("Error: rgbmatrix library not found. Please install it using the setup.sh script.")
    sys.exit(1)

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def create_config():
    print("\n--- First Time Setup ---")
    server_ip = input("Enter Server IP (default: 192.168.1.111): ").strip()
    if not server_ip:
        server_ip = "192.168.1.111"
    
    print("\n--- Matrix Configuration ---")
    print("For two 64x64 matrices chained, use rows=64, cols=64, chain=2.")
    rows = input("Enter number of rows (default 64): ").strip() or "64"
    cols = input("Enter number of cols (default 64): ").strip() or "64"
    chain = input("Enter chain length (default 2): ").strip() or "2"
    parallel = input("Enter parallel chains (default 1): ").strip() or "1"
    
    print("\nHardware Mappings: 'regular', 'adafruit-hat', 'adafruit-hat-pwm', 'compute-module', 'joy-it'")
    # Note: 'joy-it' might not be a standard mapping name in all versions, but 'adafruit-hat' is common for HATs.
    # Joy-IT often uses 'adafruit-hat' or 'regular' depending on the specific HAT.
    hardware_mapping = input("Enter hardware mapping (default 'adafruit-hat'): ").strip() or "adafruit-hat"
    
    gpio_slowdown = input("Enter GPIO slowdown (0-4, default 4 for Pi 4): ").strip() or "4"

    config = {
        "server_ip": server_ip,
        "matrix": {
            "rows": int(rows),
            "cols": int(cols),
            "chain_length": int(chain),
            "parallel": int(parallel),
            "hardware_mapping": hardware_mapping,
            "gpio_slowdown": int(gpio_slowdown)
        }
    }
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {CONFIG_FILE}")
    return config

def fetch_image(url):
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content)).convert('RGB')
    except Exception as e:
        # Print error only occasionally to avoid spamming logs? Or just print.
        # print(f"Error fetching {url}: {e}")
        pass
    return None

def main():
    # Change working directory to script directory to find config.json
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    config = load_config()
    if not config:
        config = create_config()

    options = RGBMatrixOptions()
    # Configuration from user request
    options.rows = 64
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.hardware_mapping = 'regular'
    options.gpio_slowdown = 4
    options.brightness = 50
    options.disable_hardware_pulsing = False
    options.pwm_lsb_nanoseconds = 140
    
    # Drop privileges is often problematic if not running as root, but we usually run as root.
    options.drop_privileges = False

    print("Initializing Matrix...")
    try:
        matrix = RGBMatrix(options=options)
        print(f"Matrix initialized. W: {matrix.width}, H: {matrix.height}", flush=True)
    except Exception as e:
        print(f"Failed to initialize matrix: {e}")
        print("Try running with sudo.")
        sys.exit(1)

    # Calculate dimensions
    width = options.cols * options.chain_length
    height = options.rows * options.parallel

    # Start text
    print("Displaying start text...")
    try:
        offscreen_canvas = matrix.CreateFrameCanvas()
        print("Canvas created")
    except Exception as e:
        print(f"Error creating canvas: {e}")
    
    # Create a blue background with text
    img = Image.new("RGB", (width, height), (0, 0, 50))
    draw = ImageDraw.Draw(img)
    
    # Draw text. Since we don't know if a font is available, we use default.
    # We can try to draw a big X or something if text is too small.
    try:
        # Try to load a truetype font if available on Pi
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    draw.text((5, 5), "Lemona Panel", font=font, fill=(255, 255, 0))
    draw.text((5, 25), "Starting...", font=font, fill=(0, 255, 0))
    draw.text((5, 45), f"IP: {config['server_ip']}", font=font, fill=(200, 200, 200))
    
    print("Setting image...", flush=True)
    try:
        offscreen_canvas.SetImage(img, unsafe=False)
        print("Image set.", flush=True)
    except Exception as e:
        print(f"Error setting image: {e}", flush=True)

    print("Swapping on VSync...", flush=True)
    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    print("Sleep 3...", flush=True)
    time.sleep(3)

    server_ip = config["server_ip"]
    url_a = f"http://{server_ip}:5000/api/matrix/a"
    url_b = f"http://{server_ip}:5000/api/matrix/b"

    print(f"Starting loop. Fetching from {server_ip}...")

    while True:
        start_time = time.time()
        
        img_a = fetch_image(url_a)
        img_b = fetch_image(url_b)

        if img_a is None and img_b is None:
            # If both failed, wait a bit longer before retrying to avoid spamming
            time.sleep(1)
            continue

        if img_a or img_b:
            # Create a composite image
            full_img = Image.new("RGB", (width, height), (0, 0, 0))
            
            if img_a:
                # Resize to fit one panel if needed, or just paste
                img_a = img_a.resize((options.cols, options.rows))
                full_img.paste(img_a, (0, 0))
            
            if img_b:
                img_b = img_b.resize((options.cols, options.rows))
                # Paste second image. Assuming horizontal chain.
                # If chain=2, second panel starts at cols pixels.
                full_img.paste(img_b, (options.cols, 0))
            
            offscreen_canvas.SetImage(full_img, unsafe=False)
            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        
        # Limit frame rate to avoid overloading CPU/Network
        # Sleep for remaining time to hit ~10-20 FPS or just fixed sleep
        elapsed = time.time() - start_time
        if elapsed < 0.1:
            time.sleep(0.1 - elapsed)

if __name__ == "__main__":
    main()
