#!/usr/bin/env python3
"""
Raspberry Pi LED Matrix Controller v2.1
Polls the web interface API and displays content on dual 64x64 LED matrices
Supports:
- Draw mode (real-time drawing, overrides uploads)
- Upload mode (GIF/PNG/Video files with animation)
Matrix configuration: Two 64x64 panels daisy-chained via GPIO
"""

import time
import requests
import sys
from pathlib import Path
from PIL import Image, ImageSequence
from io import BytesIO
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Configuration
API_URL = "http://45.80.148.216:8000/api/display"
API_LATEST = "http://45.80.148.216:8000/api/latest"
API_FILE = "http://45.80.148.216:8000/api/processed/"
POLL_INTERVAL = 0.01  # Check draw API frequently
POLL_LATEST_INTERVAL = 2.0  # Check for new uploads every 2 seconds
DRAW_MODE_TIMEOUT = 5.0  # Return to upload mode after 5 sec of no draw updates

class DualMatrixController:
    def __init__(self):
        # Configure matrix options (matching your working led_matrix_drawer.py)
        options = RGBMatrixOptions()
        options.rows = 64
        options.cols = 64
        options.chain_length = 2
        options.parallel = 1
        options.hardware_mapping = 'regular'
        options.gpio_slowdown = 4
        options.brightness = 50
        options.disable_hardware_pulsing = True
        options.pwm_lsb_nanoseconds = 130
        
        # Create matrix
        self.matrix = RGBMatrix(options=options)
        self.last_timestamp = None
        self.last_draw_time = None
        self.last_upload_timestamp = None
        self.current_mode = "idle"  # "draw", "upload", or "idle"
        self.gif_frames_a = []
        self.gif_frames_b = []
        self.current_frame = 0
        self.frame_duration = 100  # milliseconds
        self.last_frame_time = time.time()
        self.is_animated = False
        
        print("=" * 60)
        print("Raspberry Pi LED Matrix Controller v2.1")
        print("=" * 60)
        print(f"Matrix size: {options.rows}x{options.cols} per panel")
        print(f"Panels: {options.chain_length} (daisy-chained)")
        print(f"Total resolution: {options.cols * options.chain_length}x{options.rows}")
        print(f"Draw API: {API_URL}")
        print(f"Upload API: {API_LATEST}")
        print("=" * 60)
        
        # Show startup test pattern
        self.show_startup_pattern()
    
    def show_startup_pattern(self):
        """Display startup pattern to verify matrix works"""
        print("Showing startup pattern...")
        try:
            self.matrix.Clear()
            time.sleep(0.3)
            
            # Draw "START" text
            text_data = [
                [0, 1, 1, 1, 0,  0, 0,  1, 1, 1, 0, 0,  1, 0, 0, 1,  1, 1, 1, 0, 0,  1, 1, 1, 0],
                [1, 0, 0, 0, 0,  0, 0,  0, 1, 0, 0, 0,  1, 0, 1, 0,  1, 0, 0, 1, 0,  0, 1, 0, 0],
                [0, 1, 1, 0, 0,  0, 0,  0, 1, 0, 0, 0,  1, 1, 0, 0,  1, 1, 1, 0, 0,  0, 1, 0, 0],
                [0, 0, 0, 1, 0,  0, 0,  0, 1, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0, 0,  0, 1, 0, 0],
                [1, 1, 1, 0, 0,  0, 0,  0, 1, 0, 0, 0,  1, 0, 0, 1,  1, 0, 0, 1, 0,  0, 1, 0, 0],
            ]
            
            start_x, start_y = 20, 30
            for row_idx, row in enumerate(text_data):
                for col_idx, pixel in enumerate(row):
                    if pixel == 1:
                        self.matrix.SetPixel(start_x + col_idx, start_y + row_idx, 0, 255, 0)
            
            print("✓ Startup pattern displayed! Matrix is working!")
            time.sleep(2)
            self.matrix.Clear()
        except Exception as e:
            print(f"Error showing startup pattern: {e}")
    
    def set_pixel(self, x, y, r, g, b):
        """Set a single pixel color"""
        if 0 <= x < 128 and 0 <= y < 64:
            self.matrix.SetPixel(x, y, int(r), int(g), int(b))
    
    def display_matrices(self, matrix_a, matrix_b):
        """Display both 64x64 matrices from API data"""
        try:
            for y in range(64):
                for x in range(64):
                    rgb = matrix_a[y][x]
                    self.set_pixel(x, y, rgb[0], rgb[1], rgb[2])
            
            for y in range(64):
                for x in range(64):
                    rgb = matrix_b[y][x]
                    self.set_pixel(x + 64, y, rgb[0], rgb[1], rgb[2])
        except Exception as e:
            print(f"Error displaying matrices: {e}")
    
    def clear_display(self):
        """Clear the entire display"""
        self.matrix.Clear()
    
    def load_image_from_url(self, url):
        """Download and load an image from URL"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                return img.convert('RGB')
            return None
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            return None
    
    def load_gif_frames(self, url):
        """Download and extract all frames from a GIF"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                frames = []
                durations = []
                
                for frame in ImageSequence.Iterator(img):
                    frames.append(frame.convert('RGB'))
                    durations.append(frame.info.get('duration', 100))
                
                return frames, durations
            return None, None
        except Exception as e:
            print(f"Error loading GIF from {url}: {e}")
            return None, None
    
    def display_image(self, img_a, img_b):
        """Display two images side by side"""
        try:
            if img_a and img_a.size != (64, 64):
                img_a = img_a.resize((64, 64))
            if img_b and img_b.size != (64, 64):
                img_b = img_b.resize((64, 64))
            
            if img_a:
                for y in range(64):
                    for x in range(64):
                        r, g, b = img_a.getpixel((x, y))
                        self.matrix.SetPixel(x, y, r, g, b)
            
            if img_b:
                for y in range(64):
                    for x in range(64):
                        r, g, b = img_b.getpixel((x, y))
                        self.matrix.SetPixel(x + 64, y, r, g, b)
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    def fetch_display_data(self):
        """Fetch display data from the draw API"""
        try:
            response = requests.get(API_URL, timeout=1)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def fetch_latest_upload(self):
        """Fetch latest upload metadata"""
        try:
            response = requests.get(API_LATEST, timeout=1)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def run(self):
        """Main loop - monitor both draw API and upload API"""
        print("Starting main loop... Press Ctrl+C to exit")
        print("✓ Monitoring draw mode (real-time)")
        print("✓ Monitoring upload mode (images/GIFs)\n")
        
        last_upload_check = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Check for new uploads periodically
                if current_time - last_upload_check >= POLL_LATEST_INTERVAL:
                    upload_data = self.fetch_latest_upload()
                    
                    if upload_data and upload_data.get('timestamp') != self.last_upload_timestamp:
                        self.last_upload_timestamp = upload_data.get('timestamp')
                        file_type = upload_data.get('type')
                        files = upload_data.get('files', [])
                        
                        if len(files) >= 2:
                            print(f"\n[UPLOAD MODE] New {file_type} detected: {files}")
                            self.current_mode = "upload"
                            
                            if file_type == 'gif':
                                print("Loading GIF frames...")
                                self.gif_frames_a, durations_a = self.load_gif_frames(API_FILE + files[0])
                                self.gif_frames_b, durations_b = self.load_gif_frames(API_FILE + files[1])
                                
                                if self.gif_frames_a and self.gif_frames_b:
                                    self.frame_duration = durations_a[0] if durations_a else 100
                                    self.current_frame = 0
                                    print(f"✓ Loaded {len(self.gif_frames_a)} frames, {self.frame_duration}ms/frame")
                                else:
                                    print("✗ Failed to load GIF frames")
                                    self.current_mode = "draw"
                            else:
                                # Static image
                                print("Loading static images...")
                                img_a = self.load_image_from_url(API_FILE + files[0])
                                img_b = self.load_image_from_url(API_FILE + files[1])
                                
                                if img_a and img_b:
                                    self.display_image(img_a, img_b)
                                    print("✓ Static images displayed")
                                else:
                                    print("✗ Failed to load images")
                    
                    last_upload_check = current_time
                
                # Handle display based on mode
                if self.current_mode == "upload" and self.gif_frames_a and self.gif_frames_b:
                    # Animate GIF
                    if current_time - self.last_frame_time >= (self.frame_duration / 1000.0):
                        self.display_image(
                            self.gif_frames_a[self.current_frame],
                            self.gif_frames_b[self.current_frame]
                        )
                        self.current_frame = (self.current_frame + 1) % len(self.gif_frames_a)
                        self.last_frame_time = current_time
                
                elif self.current_mode == "draw":
                    # Check draw API for real-time drawing
                    data = self.fetch_display_data()
                    
                    if data:
                        timestamp = data.get('last_updated')
                        
                        if timestamp and timestamp != self.last_timestamp:
                            matrix_a = data.get('matrixA')
                            matrix_b = data.get('matrixB')
                            
                            if matrix_a and matrix_b:
                                print(f"[DRAW MODE] Updating display...")
                                self.display_matrices(matrix_a, matrix_b)
                                self.last_timestamp = timestamp
                
                # Small delay
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            self.clear_display()
            print("✓ Display cleared. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            self.clear_display()
            sys.exit(1)


def main():
    """Entry point"""
    controller = DualMatrixController()
    controller.run()


if __name__ == "__main__":
    main()
