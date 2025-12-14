#!/usr/bin/env python3
import os
import sys
import time
import threading
import cv2
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np

import json
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Check for simulation mode
FORCE_SIMULATION = "--no-hardware" in sys.argv or "-s" in sys.argv

try:
    if FORCE_SIMULATION:
        raise ImportError("Simulation mode forced")
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: rgbmatrix library not available. Running in simulation mode.")

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['UPLOAD_FOLDER'] = 'web/static/live_cache'
app.config['SD_CARD_FOLDER'] = 'web/static/sd_card'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['SECRET_KEY'] = 'led-matrix-secret-key-change-this'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin=False, is_approved=False):
        self.id = str(id)
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.is_approved = is_approved

    @staticmethod
    def get(user_id):
        users = load_users()
        user_data = users.get(str(user_id))
        if user_data:
            return User(
                user_id,
                user_data['username'],
                user_data['password_hash'],
                user_data.get('is_admin', False),
                user_data.get('is_approved', False)
            )
        return None

    @staticmethod
    def find_by_username(username):
        users = load_users()
        for uid, data in users.items():
            if data['username'] == username:
                return User(
                    uid,
                    data['username'],
                    data['password_hash'],
                    data.get('is_admin', False),
                    data.get('is_approved', False)
                )
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SD_CARD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except:
        return {}

class MatrixController:
    def __init__(self):
        global GPIO_AVAILABLE
        self.matrix = None
        self.offscreen_canvas = None
        self.current_mode = "color" # color, image, video
        self.current_color = (0, 0, 0)
        self.current_image = None
        self.current_video_path = None
        self.current_video_mode = 'clone'
        self.slideshow_files = []
        self.slideshow_index = 0
        self.slide_duration = 10
        self.panel_rotations = [0, 0]
        self.panel_mirrors = [False, False]
        self.last_hw_settings = {}
        self.is_running = True
        self.matrix_lock = threading.Lock()
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        
        self.init_matrix()
        self.thread.start()

    def init_matrix(self):
        global GPIO_AVAILABLE
        if GPIO_AVAILABLE:
            settings = load_settings()
            hw_settings = settings.get('hardware', {})
            self.panel_rotations = settings.get('client', {}).get('panel_rotations', [0, 0])
            self.panel_mirrors = settings.get('client', {}).get('panel_mirrors', [False, False])
            
            # Check if hardware settings actually changed
            if hw_settings == self.last_hw_settings and self.matrix is not None:
                return True
            
            options = RGBMatrixOptions()
            options.rows = hw_settings.get('rows', 64)
            options.cols = hw_settings.get('cols', 64)
            options.chain_length = hw_settings.get('chain_length', 2)
            options.parallel = hw_settings.get('parallel', 1)
            options.hardware_mapping = hw_settings.get('hardware_mapping', 'regular')
            options.gpio_slowdown = hw_settings.get('gpio_slowdown', 4)
            options.brightness = hw_settings.get('brightness', 50)
            options.pwm_lsb_nanoseconds = hw_settings.get('pwm_lsb_nanoseconds', 130)
            options.disable_hardware_pulsing = hw_settings.get('disable_hardware_pulsing', True)
            options.scan_mode = hw_settings.get('scan_mode', 0)
            options.multiplexing = hw_settings.get('multiplexing', 0)
            options.row_address_type = hw_settings.get('row_address_type', 0)
            options.pwm_bits = hw_settings.get('pwm_bits', 11)
            options.limit_refresh_rate_hz = hw_settings.get('limit_refresh_rate_hz', 0)
            
            try:
                with self.matrix_lock:
                    # Clean up old matrix if exists to free resources
                    if self.matrix:
                        self.matrix.Clear()
                        del self.matrix
                        self.matrix = None

                    self.matrix = RGBMatrix(options=options)
                    self.offscreen_canvas = self.matrix.CreateFrameCanvas()
                    self.last_hw_settings = hw_settings
                    
                    # Restore current image if needed
                    if self.current_mode == "image" and self.current_image:
                        self._safe_set_image(self.offscreen_canvas, self.current_image)
                        
                return True
            except Exception as e:
                print(f"Error initializing matrix: {e}")
                # If this is the first init (self.matrix is None), we might want to disable GPIO
                # But if it's a re-init, we should propagate error
                if self.matrix is None and not hasattr(self, 'thread'): # Heuristic for first run
                     GPIO_AVAILABLE = False
                return False
        return False

    def set_rotations(self, rotations):
        with self.matrix_lock:
            self.panel_rotations = rotations
            # Force redraw if static image
            if self.current_mode == "image" and self.current_image:
                self._safe_set_image(self.offscreen_canvas, self.current_image)
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def set_mirrors(self, mirrors):
        with self.matrix_lock:
            self.panel_mirrors = mirrors
            # Force redraw if static image
            if self.current_mode == "image" and self.current_image:
                self._safe_set_image(self.offscreen_canvas, self.current_image)
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def _apply_rotation(self, img, rotation):
        if rotation == 0: return img
        return img.rotate(-rotation, expand=False) # Negative for clockwise visual effect if needed, or just standard rotate

    def _safe_set_image(self, canvas, image, mode='split'):
        """Safely set image on canvas by setting pixels manually to avoid segfaults"""
        try:
            # Ensure image is RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create a black canvas-sized image to compose onto
            final_img = Image.new('RGB', (canvas.width, canvas.height), (0,0,0))
            
            # Split and rotate logic assuming 2x 64x64 panels side-by-side
            # Panel 1: 0-64
            # Panel 2: 64-128
            
            # Crop parts from source image
            # If source is smaller, we center it? Or just paste?
            # The source 'image' passed here is usually already resized/thumbnail to 128x64 in set_image
            
            # We need to handle the case where image is smaller than canvas
            # But let's assume we work on the canvas coordinate space
            
            # Paste source onto a temp buffer of canvas size
            temp_bg = Image.new('RGB', (canvas.width, canvas.height), (0,0,0))
            temp_bg.paste(image, (0, 0)) # Assuming image is already positioned/sized or we just paste at 0,0
            
            # Process Panel 1
            p1 = temp_bg.crop((0, 0, 64, 64))
            if len(self.panel_rotations) > 0 and self.panel_rotations[0] != 0:
                p1 = p1.rotate(-self.panel_rotations[0]) # PIL rotate is counter-clockwise, so negative for clockwise
            if len(self.panel_mirrors) > 0 and self.panel_mirrors[0]:
                p1 = p1.transpose(Image.FLIP_LEFT_RIGHT)
            final_img.paste(p1, (0, 0))
            
            # Process Panel 2
            if canvas.width >= 128:
                p2 = temp_bg.crop((64, 0, 128, 64))
                if len(self.panel_rotations) > 1 and self.panel_rotations[1] != 0:
                    p2 = p2.rotate(-self.panel_rotations[1])
                if len(self.panel_mirrors) > 1 and self.panel_mirrors[1]:
                    p2 = p2.transpose(Image.FLIP_LEFT_RIGHT)
                final_img.paste(p2, (64, 0))
            
            width, height = final_img.size
            width = min(width, canvas.width)
            height = min(height, canvas.height)
            
            # Use SetImage instead of manual pixel loop for performance
            # Reverting to manual loop as SetImage caused SEGV
            pixels = final_img.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    canvas.SetPixel(x, y, r, g, b)
        except Exception as e:
            print(f"Error in _safe_set_image: {e}")

    def _run_loop(self):
        last_image_update = 0
        while self.is_running:
            try:
                if not GPIO_AVAILABLE:
                    time.sleep(1)
                    continue
                
                with self.matrix_lock:
                    if not self.matrix or not self.offscreen_canvas:
                        time.sleep(0.1)
                        continue

                    if self.current_mode == "color":
                        self.offscreen_canvas.Fill(self.current_color[0], self.current_color[1], self.current_color[2])
                        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                        time.sleep(0.1)
                    
                    elif self.current_mode == "image":
                        # Only update if we haven't drawn this frame yet or if we need to refresh
                        # Actually, SwapOnVSync swaps buffers, so we need to draw to the new back buffer.
                        # But if the image is static, we don't need to swap at all!
                        # We can just draw once and wait.
                        
                        # However, if we just set it and forget it, any other draw operation (like from another thread?)
                        # No, we are the only thread drawing.
                        
                        # Optimization: If mode is image and we already drew it, just sleep.
                        # We need a flag to know if we need to redraw (e.g. rotation changed).
                        # But set_rotations calls _safe_set_image directly to force update.
                        # So here in the loop, we can just sleep if it's static image.
                        
                        time.sleep(0.1)
                    
                    elif self.current_mode == "video":
                        if self.current_video_path:
                            # Release lock for video playback as it has its own loop
                            # But wait, _play_video needs the lock too?
                            # If we release lock here, init_matrix might run.
                            # If we hold lock here, init_matrix will block until video is done?
                            # Video playback is a loop. We shouldn't block init_matrix for the whole video.
                            pass
                        else:
                            time.sleep(0.1)
                    
                    elif self.current_mode == "slideshow":
                        # Same issue as video
                        pass
                    
                    elif self.current_mode == "draw":
                        # Drawing is handled by event updates, just keep display active
                        time.sleep(0.1)
                
                # Handle long running modes outside the main lock, but they need to check lock internally
                if self.current_mode == "video" and self.current_video_path:
                    self._play_video(self.current_video_path, mode=self.current_video_mode)
                elif self.current_mode == "slideshow":
                    self._run_slideshow_step()
                    
            except Exception as e:
                print(f"Error in run loop: {e}")
                time.sleep(1)

    def _run_slideshow_step(self):
        if not self.slideshow_files:
            self.current_mode = "color"
            return

        try:
            file = self.slideshow_files[self.slideshow_index]
            filepath = os.path.join('web/static/sd_card', file)
            
            if not os.path.exists(filepath):
                # Skip missing files
                self.slideshow_index = (self.slideshow_index + 1) % len(self.slideshow_files)
                return

            # Try to load config
            mode = 'clone'
            config_path = filepath + '.json'
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        mode = config.get('mode', 'clone')
                except:
                    pass

            ext = file.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png']:
                try:
                    bg = self._process_image(filepath, mode)
                    
                    with self.matrix_lock:
                        if self.matrix and self.offscreen_canvas:
                            self._safe_set_image(self.offscreen_canvas, bg, mode)
                            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                    time.sleep(self.slide_duration)
                except Exception as e:
                    print(f"Error showing slide {file}: {e}")
            elif ext in ['gif', 'mp4']:
                # Play video with duration limit, loop=True to fill the duration
                self._play_video(filepath, loop=True, mode=mode, duration_limit=self.slide_duration)
            
            self.slideshow_index = (self.slideshow_index + 1) % len(self.slideshow_files)
        except Exception as e:
            print(f"Error in slideshow step: {e}")
            time.sleep(1)

    def _play_video(self, path, loop=True, mode='clone', duration_limit=None):
        try:
            ext = path.split('.')[-1].lower()
            start_time = time.time()
            
            if ext == 'gif':
                try:
                    gif = Image.open(path)
                    frames = []
                    try:
                        while True:
                            # Pre-process frames
                            frame = gif.copy().convert('RGB')
                            frames.append((frame, gif.info.get('duration', 100) / 1000.0))
                            gif.seek(gif.tell() + 1)
                    except EOFError:
                        pass
                    
                    if not frames:
                        print("No frames found in GIF")
                        if self.current_mode == "video": self.current_mode = "color"
                        return

                    # Play loop
                    while (self.current_mode == "video" and self.current_video_path == path) or (self.current_mode == "slideshow"):
                        if duration_limit and (time.time() - start_time > duration_limit):
                            return

                        for frame, duration in frames:
                            if (self.current_mode == "video" and self.current_video_path != path) or (self.current_mode != "video" and self.current_mode != "slideshow"):
                                return
                            
                            if duration_limit and (time.time() - start_time > duration_limit):
                                return
                            
                            # Resize/Compose frame based on mode
                            pil_img = frame
                            if mode == 'split':
                                pil_img = pil_img.resize((128, 64))
                            else:
                                # Clone, Matrix A, Matrix B -> Target is 64x64
                                small_img = pil_img.resize((64, 64))
                                bg = Image.new('RGB', (128, 64), (0, 0, 0))
                                if mode == 'clone':
                                    bg.paste(small_img, (0, 0))
                                    bg.paste(small_img, (64, 0))
                                elif mode == 'matrix_a':
                                    bg.paste(small_img, (0, 0))
                                elif mode == 'matrix_b':
                                    bg.paste(small_img, (64, 0))
                                pil_img = bg

                            with self.matrix_lock:
                                if self.matrix and self.offscreen_canvas:
                                    self._safe_set_image(self.offscreen_canvas, pil_img, mode)
                                    self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                            
                            time.sleep(duration)
                        
                        if not loop:
                            return

                except Exception as e:
                    print(f"Error playing GIF: {e}")
                    time.sleep(1)

            elif ext == 'mp4':
                try:
                    cap = cv2.VideoCapture(path)
                    if not cap.isOpened():
                        print(f"Failed to open video: {path}")
                        if self.current_mode == "video": self.current_mode = "color"
                        return

                    fps = cap.get(cv2.CAP_PROP_FPS)
                    if fps <= 0: fps = 30
                    delay = 1.0 / fps
                    
                    while (self.current_mode == "video" and self.current_video_path == path and cap.isOpened()) or (self.current_mode == "slideshow" and cap.isOpened()):
                        if duration_limit and (time.time() - start_time > duration_limit):
                            break

                        ret, frame = cap.read()
                        if not ret:
                            if loop:
                                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                continue
                            else:
                                break
                        
                        try:
                            # Convert BGR to RGB
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_img = Image.fromarray(frame)
                            
                            # Resize logic based on mode
                            if mode == 'split':
                                pil_img = pil_img.resize((128, 64))
                            else:
                                # Clone, Matrix A, Matrix B -> Target is 64x64
                                small_img = pil_img.resize((64, 64))
                                bg = Image.new('RGB', (128, 64), (0, 0, 0))
                                if mode == 'clone':
                                    bg.paste(small_img, (0, 0))
                                    bg.paste(small_img, (64, 0))
                                elif mode == 'matrix_a':
                                    bg.paste(small_img, (0, 0))
                                elif mode == 'matrix_b':
                                    bg.paste(small_img, (64, 0))
                                pil_img = bg
                            
                            with self.matrix_lock:
                                if self.matrix and self.offscreen_canvas:
                                    self._safe_set_image(self.offscreen_canvas, pil_img, mode)
                                    self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                        except Exception as e:
                            print(f"Error processing frame: {e}")
                        
                        time.sleep(delay)
                    cap.release()
                except Exception as e:
                    print(f"Error playing MP4: {e}")
        except Exception as e:
            print(f"Critical error in _play_video: {e}")
            time.sleep(1)

    def set_color(self, r, g, b):
        self.current_mode = "color"
        self.current_color = (r, g, b)

    def _process_image(self, image_path, mode='clone'):
        img = Image.open(image_path)
        
        # Safety check for very large images to prevent OOM
        if img.width > 4000 or img.height > 4000:
            print("Image too large, resizing before processing")
            img.thumbnail((2000, 2000))

        bg = Image.new('RGB', (128, 64), (0, 0, 0))

        if mode == 'split':
            img.thumbnail((128, 64), Image.Resampling.LANCZOS)
            x = (128 - img.width) // 2
            y = (64 - img.height) // 2
            bg.paste(img, (x, y))
        else:
            # Clone, Matrix A, Matrix B -> Target is 64x64
            img.thumbnail((64, 64), Image.Resampling.LANCZOS)
            x = (64 - img.width) // 2
            y = (64 - img.height) // 2
            
            if mode == 'clone':
                bg.paste(img, (x, y))      # Left
                bg.paste(img, (x + 64, y)) # Right
            elif mode == 'matrix_a':
                bg.paste(img, (x, y))      # Left
            elif mode == 'matrix_b':
                bg.paste(img, (x + 64, y)) # Right
        return bg

    def set_image(self, image_path, mode='clone'):
        try:
            bg = self._process_image(image_path, mode)
            
            self.current_image = bg
            self.current_mode = "image"
            
            # Force immediate update
            with self.matrix_lock:
                if self.matrix and self.offscreen_canvas:
                    self._safe_set_image(self.offscreen_canvas, self.current_image, mode)
                    self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                    
        except Exception as e:
            print(f"Error setting image: {e}")

    def set_video(self, video_path, mode='clone'):
        self.current_video_path = video_path
        self.current_video_mode = mode
        self.current_mode = "video"

    def clear(self):
        self.set_color(0, 0, 0)

    def set_slideshow(self, files, duration):
        self.slideshow_files = files
        self.slide_duration = float(duration)
        self.slideshow_index = 0
        self.current_mode = "slideshow"

    def set_rotations(self, rotations):
        """Set panel rotations for each panel in the matrix"""
        # This is a no-op in the base class, meant to be overridden if needed
        pass

matrix_controller = MatrixController()

# Auth Decorators
def approved_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
             return redirect(url_for('login'))
        if not current_user.is_approved:
            flash('Your account is pending approval.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.find_by_username(username)
        
        if user and user.check_password(password):
            if not user.is_approved:
                flash('Account pending approval.')
                return render_template('login.html')
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            flash('Passwords do not match')
            return render_template('register.html')
            
        if User.find_by_username(username):
            flash('Username already exists')
            return render_template('register.html')
            
        users = load_users()
        # First user is admin and approved
        is_first_user = len(users) == 0
        
        new_id = str(int(max(users.keys(), key=int)) + 1) if users else "1"
        
        users[new_id] = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'is_admin': is_first_user,
            'is_approved': is_first_user
        }
        save_users(users)
        
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    users = load_users()
    return jsonify([{
        'id': uid,
        'username': data['username'],
        'is_admin': data.get('is_admin', False),
        'is_approved': data.get('is_approved', False)
    } for uid, data in users.items()])

@app.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
def admin_approve(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = load_users()
    uid = str(user_id)
    if uid in users:
        users[uid]['is_approved'] = True
        save_users(users)
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_admin(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = load_users()
    uid = str(user_id)
    if uid in users:
        if uid == current_user.id:
             return jsonify({'error': 'Cannot change own admin status'}), 400
        users[uid]['is_admin'] = not users[uid].get('is_admin', False)
        save_users(users)
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = load_users()
    uid = str(user_id)
    if uid in users:
        if uid == current_user.id:
             return jsonify({'error': 'Cannot delete self'}), 400
        del users[uid]
        save_users(users)
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/')
@login_required
@approved_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/upload', methods=['POST'])
@login_required
@approved_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Always save/overwrite for live upload
            file.save(filepath)
            
            mode = request.form.get('mode', 'clone')
            ext = filename.rsplit('.', 1)[1].lower()
            
            if ext in ['jpg', 'jpeg', 'png']:
                matrix_controller.set_image(filepath, mode)
            elif ext in ['gif', 'mp4']:
                matrix_controller.set_video(filepath, mode)
                
            return jsonify({'success': True, 'filename': filename, 'mode': mode})
    except Exception as e:
        print(f"Error in upload_file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sd-upload', methods=['POST'])
@login_required
@approved_required
def sd_upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['SD_CARD_FOLDER'], filename)
            file.save(filepath)
            
            mode = request.form.get('mode', 'clone')
            
            # Create default config for this file
            config_path = filepath + '.json'
            config = {
                'filename': filename,
                'type': filename.rsplit('.', 1)[1].lower(),
                'duration': 10,
                'mode': mode
            }
            with open(config_path, 'w') as f:
                json.dump(config, f)
                
            return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sd-files')
@login_required
@approved_required
def get_sd_files():
    files = []
    try:
        for filename in os.listdir(app.config['SD_CARD_FOLDER']):
            if allowed_file(filename):
                files.append(filename)
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/play-sd', methods=['POST'])
@login_required
@approved_required
def play_sd_file():
    try:
        data = request.json
        filename = data.get('filename')
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
            
        filepath = os.path.join(app.config['SD_CARD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
            
        if not allowed_file(filename):
            return jsonify({'error': 'Invalid file type'}), 400
            
        # Try to load config
        mode = 'clone'
        config_path = filepath + '.json'
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    mode = config.get('mode', 'clone')
            except:
                pass

        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ['jpg', 'jpeg', 'png']:
            matrix_controller.set_image(filepath, mode)
        elif ext in ['gif', 'mp4']:
            matrix_controller.set_video(filepath, mode)
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings', methods=['GET', 'POST'])
@login_required
@approved_required
def settings():
    if request.method == 'POST':
        backup_settings = None
        try:
            # Backup current settings
            try:
                with open('settings.json', 'r') as f:
                    backup_settings = json.load(f)
            except:
                backup_settings = {}

            flat_data = request.json
            
            # Reconstruct structure
            # Preserve existing rotations as they are not in the form
            current_settings = load_settings()
            current_rotations = current_settings.get('client', {}).get('panel_rotations', [0, 0])
            current_mirrors = current_settings.get('client', {}).get('panel_mirrors', [False, False])

            new_settings = {
                "hardware": {
                    "rows": int(flat_data.get('rows', 64)),
                    "cols": int(flat_data.get('cols', 64)),
                    "chain_length": int(flat_data.get('chain_length', 2)),
                    "parallel": int(flat_data.get('parallel', 1)),
                    "hardware_mapping": flat_data.get('hardware_mapping', 'regular'),
                    "gpio_slowdown": int(flat_data.get('gpio_slowdown', 4)),
                    "pwm_lsb_nanoseconds": int(flat_data.get('pwm_lsb', 130)),
                    "brightness": int(flat_data.get('brightness', 50)),
                    "disable_hardware_pulsing": flat_data.get('hardware_pulsing') == 'on' or flat_data.get('hardware_pulsing') is True,
                    "scan_mode": int(flat_data.get('scan_mode', 0)),
                    "multiplexing": int(flat_data.get('multiplexing', 0)),
                    "row_address_type": int(flat_data.get('row_address_type', 0)),
                    "pwm_bits": int(flat_data.get('pwm_bits', 11)),
                    "limit_refresh_rate_hz": int(flat_data.get('limit_refresh_rate_hz', 0))
                },
                "client": {
                    "brightness": int(flat_data.get('brightness', 50)),
                    "slide_duration": float(flat_data.get('slide_duration', 10)),
                    "panel_rotations": current_rotations,
                    "panel_mirrors": current_mirrors
                }
            }
            
            with open('settings.json', 'w') as f:
                json.dump(new_settings, f, indent=4)
            
            # Re-init matrix with new settings
            if not matrix_controller.init_matrix():
                raise Exception("Hardware initialization failed")
                
            return jsonify({'success': True})
        except Exception as e:
            print(f"Settings error: {e}")
            # Restore settings if we have a backup
            if backup_settings:
                with open('settings.json', 'w') as f:
                    json.dump(backup_settings, f, indent=4)
                # Try to restore matrix state
                matrix_controller.init_matrix()
            
            # Failsafe: If we really crashed hard (e.g. segfault or unrecoverable), 
            # we might want to restart the service.
            # But here we caught the exception, so we are likely still alive.
            # If init_matrix returned False, it means RGBMatrix failed.
            
            return jsonify({'error': f"Settings rejected: {str(e)}. Reverted to previous settings."}), 400
    else:
        # Flatten for UI
        settings = load_settings()
        flat = {}
        flat.update(settings.get('hardware', {}))
        flat.update(settings.get('client', {}))
        # Map specific keys if needed
        flat['pwm_lsb'] = settings.get('hardware', {}).get('pwm_lsb_nanoseconds', 130)
        flat['hardware_pulsing'] = settings.get('hardware', {}).get('disable_hardware_pulsing', True)
        return jsonify(flat)

@app.route('/draw', methods=['POST'])
@login_required
@approved_required
def draw_pixel():
    try:
        data = request.json
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        color = data.get('color', '#000000')
        size = int(data.get('size', 1))
        
        # Convert hex to rgb
        h = color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        if matrix_controller.current_mode != "draw":
            matrix_controller.current_mode = "draw"
            # Clear canvas for drawing if switching modes
            matrix_controller.offscreen_canvas.Fill(0, 0, 0)
            
        # Draw a square of size*size
        for dx in range(size):
            for dy in range(size):
                px, py = x + dx, y + dy
                if 0 <= px < 128 and 0 <= py < 64:
                    matrix_controller.offscreen_canvas.SetPixel(px, py, rgb[0], rgb[1], rgb[2])
        
        matrix_controller.offscreen_canvas = matrix_controller.matrix.SwapOnVSync(matrix_controller.offscreen_canvas)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/color', methods=['POST'])
@login_required
@approved_required
def set_color():
    color = request.form.get('color')
    if color:
        # Convert hex to rgb
        h = color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        matrix_controller.set_color(*rgb)
    return redirect(url_for('index'))

@app.route('/clear')
@login_required
@approved_required
def clear():
    matrix_controller.clear()
    return redirect(url_for('index'))

@app.route('/delete-sd-file', methods=['POST'])
@login_required
@approved_required
def delete_sd_file():
    try:
        data = request.json
        filename = data.get('filename')
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
            
        filepath = os.path.join(app.config['SD_CARD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
            
        os.remove(filepath)
        # Also remove config if exists
        if os.path.exists(filepath + '.json'):
            os.remove(filepath + '.json')
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/play-slideshow', methods=['POST'])
@login_required
@approved_required
def play_slideshow():
    try:
        files = []
        if os.path.exists(app.config['SD_CARD_FOLDER']):
            for filename in os.listdir(app.config['SD_CARD_FOLDER']):
                if allowed_file(filename):
                    files.append(filename)
        
        if not files:
            return jsonify({'error': 'No files to play'}), 400
            
        files.sort() # Play in order
        
        # Get duration from request, fallback to settings
        data = request.get_json(silent=True) or {}
        settings = load_settings()
        duration = float(data.get('duration', 
                   settings.get('client', {}).get('slide_duration', 10)))
        
        matrix_controller.set_slideshow(files, duration)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/restart', methods=['POST'])
@login_required
@approved_required
def restart_server():
    def restart():
        time.sleep(1)
        # Restart the service
        os.system('sudo systemctl restart led-matrix.service')
    
    threading.Thread(target=restart).start()
    return jsonify({'success': True})

@app.route('/rotate-panel', methods=['POST'])
@login_required
@approved_required
def rotate_panel():
    try:
        data = request.json
        panel_idx = int(data.get('panel', 0))
        
        settings = load_settings()
        client_settings = settings.get('client', {})
        rotations = client_settings.get('panel_rotations', [0, 0])
        
        # Ensure list is long enough
        while len(rotations) <= panel_idx:
            rotations.append(0)
            
        # Rotate 90 degrees
        rotations[panel_idx] = (rotations[panel_idx] + 90) % 360
        
        client_settings['panel_rotations'] = rotations
        settings['client'] = client_settings
        
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
            
        matrix_controller.set_rotations(rotations)
        
        return jsonify({'success': True, 'rotation': rotations[panel_idx]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mirror-panel', methods=['POST'])
@login_required
@approved_required
def mirror_panel():
    try:
        data = request.json
        panel_idx = int(data.get('panel', 0))
        
        settings = load_settings()
        client_settings = settings.get('client', {})
        mirrors = client_settings.get('panel_mirrors', [False, False])
        
        # Ensure list is long enough
        while len(mirrors) <= panel_idx:
            mirrors.append(False)
            
        # Toggle mirror
        mirrors[panel_idx] = not mirrors[panel_idx]
        
        client_settings['panel_mirrors'] = mirrors
        settings['client'] = client_settings
        
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
            
        matrix_controller.set_mirrors(mirrors)
        
        return jsonify({'success': True, 'mirror': mirrors[panel_idx]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=False)
