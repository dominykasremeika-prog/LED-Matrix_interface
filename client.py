import sys
import time
import json
import os
import requests
import subprocess
import socket
import threading
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from flask import Flask, request, jsonify

# Try to import rgbmatrix. If not available, print error.
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except ImportError:
    print("Error: rgbmatrix library not found. Please install it using the setup.sh script.")
    sys.exit(1)

CONFIG_FILE = "config.json"
SD_CONTENT_DIR = "sd_content"

# Ensure SD content directory exists
if not os.path.exists(SD_CONTENT_DIR):
    os.makedirs(SD_CONTENT_DIR)

# Flask App for receiving files
app = Flask(__name__)

@app.route('/api/sd/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = file.filename
        file.save(os.path.join(SD_CONTENT_DIR, filename))
        return jsonify({"message": "File uploaded successfully"}), 200

def run_flask_server():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def get_network_info():
    info = {
        "type": "Unknown",
        "ssid": None,
        "ip": None
    }
    
    # Get IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["ip"] = s.getsockname()[0]
        s.close()
    except Exception:
        info["ip"] = "127.0.0.1"

    # Check for WiFi
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"]).decode("utf-8").strip()
        if ssid:
            info["type"] = "WiFi"
            info["ssid"] = ssid
            return info
    except Exception:
        pass

    # Check for Ethernet
    if info["ip"] != "127.0.0.1":
        info["type"] = "Ethernet"
    
    return info

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
    telemetry_url = f"http://{server_ip}:5000/api/telemetry"
    config_url = f"http://{server_ip}:5000/api/client-config"

    print(f"Starting loop. Fetching from {server_ip}...")

    # Initial settings
    current_polling_rate = 1.0
    current_request_send_rate = 1.0
    screen_rotation = 0
    use_sd_card_fallback = False

    # Fallback state
    fallback_files = []
    current_fallback_index = 0
    fallback_start_time = 0
    current_gif = None
    current_gif_frame = 0
    next_frame_time = 0

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()

    while True:
        start_time = time.time()
        
        # 1. Fetch Configuration
        try:
            config_resp = requests.get(config_url, timeout=0.5)
            if config_resp.status_code == 200:
                remote_config = config_resp.json()
                
                # Apply settings
                if "brightness" in remote_config:
                    matrix.brightness = int(remote_config["brightness"])
                
                if "polling_rate" in remote_config:
                    current_polling_rate = float(remote_config["polling_rate"])
                
                if "request_send_rate" in remote_config:
                    current_request_send_rate = float(remote_config["request_send_rate"])
                
                if "position_1" in remote_config:
                    screen_rotation = int(remote_config["position_1"])
                
                if "use_sd_card_fallback" in remote_config:
                    use_sd_card_fallback = bool(remote_config["use_sd_card_fallback"])
                
                # Note: gpio_slowdown and hardware_pulsing require restart/re-init
        except Exception:
            pass

        # 2. Telemetry Data
        telemetry = {
            "polling_rate": current_polling_rate,
            "gpio_slowdown": options.gpio_slowdown,
            "network": get_network_info(),
            "refresh_rate": 60, # Approximate
            "hardware_pulsing": not options.disable_hardware_pulsing,
            "brightness": matrix.brightness,
            "position_1": screen_rotation,
            "position_2": 0,
            "request_send_rate": current_request_send_rate
        }
        
        # Send Telemetry
        try:
            requests.post(telemetry_url, json=telemetry, timeout=0.5)
        except Exception:
            pass 

        # 3. Fetch Images
        img_a = fetch_image(url_a)
        img_b = fetch_image(url_b)

        if img_a is None and img_b is None:
            if use_sd_card_fallback:
                # Fallback Logic
                try:
                    # Refresh file list if empty or periodically? For now, just listdir.
                    # To avoid constant disk I/O, maybe only check if list is empty or every X seconds.
                    # For simplicity, let's check if we need to load a file.
                    
                    if not fallback_files:
                        fallback_files = [f for f in os.listdir(SD_CONTENT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                        fallback_files.sort()
                    
                    if fallback_files:
                        now = time.time()
                        
                        # Check if we need to switch file (30s timer)
                        if now - fallback_start_time > 30 or current_gif is None:
                            fallback_start_time = now
                            current_fallback_index = (current_fallback_index + 1) % len(fallback_files)
                            filename = fallback_files[current_fallback_index]
                            filepath = os.path.join(SD_CONTENT_DIR, filename)
                            try:
                                current_gif = Image.open(filepath)
                                current_gif_frame = 0
                                next_frame_time = 0
                            except Exception as e:
                                print(f"Error loading fallback file {filename}: {e}")
                                current_gif = None
                        
                        if current_gif:
                            # Handle GIF animation
                            if getattr(current_gif, "is_animated", False):
                                if now >= next_frame_time:
                                    current_gif.seek(current_gif_frame)
                                    duration = current_gif.info.get('duration', 100) / 1000.0
                                    next_frame_time = now + duration
                                    current_gif_frame = (current_gif_frame + 1) % current_gif.n_frames
                            
                            # Create full image from fallback content
                            full_img = Image.new("RGB", (width, height), (0, 0, 0))
                            
                            # Resize/Crop logic: Fit to screen
                            # For now, simple resize
                            frame = current_gif.convert("RGB")
                            frame = frame.resize((width, height))
                            full_img.paste(frame, (0, 0))
                            
                            # Apply rotation
                            if screen_rotation != 0:
                                full_img = full_img.rotate(screen_rotation, expand=True)
                                if full_img.size != (width, height):
                                     full_img = full_img.resize((width, height))

                            offscreen_canvas.SetImage(full_img, unsafe=False)
                            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                            
                            # Short sleep for loop, but GIF timing handles frame rate
                            time.sleep(0.01) 
                            continue
                except Exception as e:
                    print(f"Fallback error: {e}")
            
            # If no fallback or failed, sleep
            time.sleep(1)
            continue
        
        # Reset fallback state if we have active content
        current_gif = None

        if img_a or img_b:
            # Create a composite image
            full_img = Image.new("RGB", (width, height), (0, 0, 0))
            
            if img_a:
                # Resize to fit one panel if needed, or just paste
                img_a = img_a.resize((options.cols, options.rows))
                full_img.paste(img_a, (0, 0))
            
            if img_b:
                img_b = img_b.resize((options.cols, options.rows))
                full_img.paste(img_b, (options.cols, 0))
            
            # Apply rotation
            if screen_rotation != 0:
                full_img = full_img.rotate(screen_rotation, expand=True)
                if full_img.size != (width, height):
                     full_img = full_img.resize((width, height))

            offscreen_canvas.SetImage(full_img, unsafe=False)
            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        
        # Limit frame rate based on request_send_rate
        delay = 1.0 / current_request_send_rate if current_request_send_rate > 0 else 1.0
        elapsed = time.time() - start_time
        if elapsed < delay:
            time.sleep(delay - elapsed)

if __name__ == "__main__":
    main()
