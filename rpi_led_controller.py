#!/usr/bin/env python3
"""
Raspberry Pi LED Matrix Controller v2.2
Polls the web interface API and displays content on dual 64x64 LED matrices
Supports:
- Draw mode (real-time drawing, overrides uploads)
- Upload mode (GIF/PNG/Video files with animation)
Matrix configuration: Two 64x64 panels daisy-chained via GPIO
"""

import time
import requests
import sys
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageSequence
from io import BytesIO
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Configuration
API_URL = "http://45.80.148.216:8000/api/display"
API_LATEST = "http://45.80.148.216:8000/api/latest"
API_FILE = "http://45.80.148.216:8000/api/processed/"
POLL_DRAW_INTERVAL = 0.5  # Check draw API every 500ms (reduced from 200ms)
POLL_LATEST_INTERVAL = 5.0  # Check for new uploads every 5 seconds (reduced from 3s)

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
        self.last_draw_check = 0
        self.last_displayed_data = None  # Cache to prevent redundant refreshes
        self.last_displayed_draw_timestamp = None  # Track what we last displayed for draw mode
        self.last_displayed_upload_timestamp = None  # Track what we last displayed for upload mode
        self.last_draw_content_hash = None  # Hash of the last draw content displayed
        self.last_upload_content_hash = None  # Hash of the last upload content displayed
        
        print("=" * 60)
        print("Raspberry Pi LED Matrix Controller v2.2")
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
    
    def compute_content_hash(self, data):
        """Compute a hash of the content to detect actual changes"""
        try:
            # Convert data to string and hash it
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
        except:
            return None
    
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
        print("✓ Displays whichever is most recently updated: drawings or uploads")
        print("✓ Only updates when new data is received (no flashing)\n")
        
        last_upload_check = time.time()
        last_draw_timestamp_str = None
        last_upload_timestamp_str = None
        
        try:
            while True:
                current_time = time.time()
                
                # Check draw API (every 500ms)
                if current_time - self.last_draw_check >= POLL_DRAW_INTERVAL:
                    data = self.fetch_display_data()
                    
                    if data:
                        draw_timestamp = data.get('last_updated')
                        matrix_a = data.get('matrixA')
                        matrix_b = data.get('matrixB')
                        
                        if matrix_a and matrix_b:
                            # Compute hash of the actual pixel content
                            content_hash = self.compute_content_hash({'a': matrix_a, 'b': matrix_b})
                            
                            # Only update if the actual content has changed
                            if content_hash and content_hash != self.last_draw_content_hash:
                                # Compare timestamps to decide if draw should override upload
                                should_display_draw = False
                                
                                if last_upload_timestamp_str is None:
                                    # No upload yet, display draw
                                    should_display_draw = True
                                elif draw_timestamp and draw_timestamp > last_upload_timestamp_str:
                                    # Draw is newer than upload, display draw
                                    should_display_draw = True
                                elif draw_timestamp == last_draw_timestamp_str:
                                    # Same timestamp but content changed (user continued drawing)
                                    should_display_draw = True
                                
                                if should_display_draw:
                                    # Switch to draw mode and clear upload content
                                    if self.current_mode == "upload":
                                        print("[SWITCHING] Upload → Draw mode")
                                        self.gif_frames_a = []
                                        self.gif_frames_b = []
                                    
                                    self.current_mode = "draw"
                                    self.last_draw_time = current_time
                                    print(f"[DRAW MODE] Updating display (new content detected)")
                                    self.display_matrices(matrix_a, matrix_b)
                                    last_draw_timestamp_str = draw_timestamp
                                    self.last_displayed_draw_timestamp = draw_timestamp
                                    self.last_draw_content_hash = content_hash
                    
                    self.last_draw_check = current_time
                
                # Check for new uploads (every 5 seconds)
                if current_time - last_upload_check >= POLL_LATEST_INTERVAL:
                    upload_data = self.fetch_latest_upload()
                    
                    if upload_data:
                        upload_timestamp = upload_data.get('timestamp')
                        
                        # Compute hash of upload metadata to detect actual new uploads
                        upload_hash = self.compute_content_hash(upload_data)
                        
                        # Only update if the upload content has actually changed
                        if upload_hash and upload_hash != self.last_upload_content_hash:
                            # Compare timestamps to decide if upload should override draw
                            should_display_upload = False
                            
                            if last_draw_timestamp_str is None:
                                # No draw yet, display upload
                                should_display_upload = True
                            elif upload_timestamp and upload_timestamp > last_draw_timestamp_str:
                                # Upload is newer than draw, display upload
                                should_display_upload = True
                            
                            if should_display_upload:
                                file_type = upload_data.get('type')
                                files = upload_data.get('files', [])
                                
                                if len(files) >= 2:
                                    # Switch to upload mode and clear draw content
                                    if self.current_mode == "draw":
                                        print("[SWITCHING] Draw → Upload mode")
                                    
                                    print(f"\n[UPLOAD MODE] New {file_type} detected (new content)")
                                    self.current_mode = "upload"
                                    self.is_animated = (file_type == 'gif')
                                    last_upload_timestamp_str = upload_timestamp
                                    self.last_displayed_upload_timestamp = upload_timestamp
                                    self.last_upload_content_hash = upload_hash
                                    
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
                                            self.current_mode = "idle"
                                    else:
                                        # Static image - display once
                                        print("Loading static images...")
                                        img_a = self.load_image_from_url(API_FILE + files[0])
                                        img_b = self.load_image_from_url(API_FILE + files[1])
                                        
                                        if img_a and img_b:
                                            self.display_image(img_a, img_b)
                                            print("✓ Static images displayed")
                                        else:
                                            print("✗ Failed to load images")
                    
                    last_upload_check = current_time
                
                # Animate GIF if in upload mode
                if self.current_mode == "upload" and self.is_animated and self.gif_frames_a and self.gif_frames_b:
                    if current_time - self.last_frame_time >= (self.frame_duration / 1000.0):
                        self.display_image(
                            self.gif_frames_a[self.current_frame],
                            self.gif_frames_b[self.current_frame]
                        )
                        self.current_frame = (self.current_frame + 1) % len(self.gif_frames_a)
                        self.last_frame_time = current_time
                
                # Adaptive sleep based on mode
                if self.is_animated and self.current_mode == "upload":
                    time.sleep(0.02)  # Fast loop for animations (20ms)
                else:
                    time.sleep(0.1)  # Slower for static/draw mode (100ms)
                
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
