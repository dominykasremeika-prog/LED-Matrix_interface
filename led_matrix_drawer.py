#!/usr/bin/env python3
"""
LED Matrix Drawing Application
Draw on a 64x64 canvas and display on RGB LED matrix panels via GPIO
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import json
import numpy as np
from PIL import Image, ImageDraw
import threading
import time

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: rgbmatrix library not available. Running in simulation mode.")


class LEDMatrixDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("LED Matrix Drawer - 64x64")
        self.root.geometry("900x700")
        
        # Canvas settings
        self.panel_width = 64
        self.panel_height = 64
        self.total_width = 128  # Two 64x64 panels
        self.total_height = 64
        self.pixel_size = 6  # Smaller GUI pixel size to fit both panels
        
        # Drawing state
        self.current_color = "#FF0000"  # Red
        self.drawing = False
        self.pixel_data = np.zeros((self.total_height, self.total_width, 3), dtype=np.uint8)
        
        # Undo/Redo functionality
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_levels = 50  # Limit undo history to save memory
        
        # Drawing optimization - lower polling rate
        self.last_draw_time = 0
        self.draw_throttle = 0.016  # ~60fps (16ms between updates)
        
        # LED Matrix settings
        self.matrix = None
        self.matrix_enabled = False
        self.update_thread = None
        self.running = False
        
        self.setup_ui()
        self.initialize_matrix()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tool panel
        tool_frame = ttk.LabelFrame(main_frame, text="Tools", padding="10")
        tool_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Color picker
        ttk.Label(tool_frame, text="Color:").grid(row=0, column=0, pady=5)
        self.color_display = tk.Canvas(tool_frame, width=50, height=50, bg=self.current_color)
        self.color_display.grid(row=1, column=0, pady=5)
        ttk.Button(tool_frame, text="Choose Color", command=self.choose_color).grid(row=2, column=0, pady=5)
        
        # Quick colors
        ttk.Label(tool_frame, text="Quick Colors:").grid(row=3, column=0, pady=(15, 5))
        quick_colors = [
            ("#FF0000", "Red"),
            ("#00FF00", "Green"),
            ("#0000FF", "Blue"),
            ("#FFFF00", "Yellow"),
            ("#FF00FF", "Magenta"),
            ("#00FFFF", "Cyan"),
            ("#FFFFFF", "White"),
            ("#000000", "Black")
        ]
        
        for idx, (color, name) in enumerate(quick_colors):
            btn = tk.Button(tool_frame, bg=color, width=6, height=2,
                          command=lambda c=color: self.set_color(c))
            btn.grid(row=4+idx//2, column=0, pady=2)
        
        # Tools
        ttk.Separator(tool_frame, orient='horizontal').grid(row=12, column=0, sticky='ew', pady=10)
        ttk.Button(tool_frame, text="Clear Canvas", command=self.clear_canvas).grid(row=13, column=0, pady=5)
        ttk.Button(tool_frame, text="Fill Canvas", command=self.fill_canvas).grid(row=14, column=0, pady=5)
        
        # Undo/Redo
        ttk.Separator(tool_frame, orient='horizontal').grid(row=15, column=0, sticky='ew', pady=10)
        ttk.Button(tool_frame, text="⟲ Undo (Ctrl+Z)", command=self.undo).grid(row=16, column=0, pady=5)
        ttk.Button(tool_frame, text="⟳ Redo (Ctrl+Y)", command=self.redo).grid(row=17, column=0, pady=5)
        
        # Save/Load
        ttk.Separator(tool_frame, orient='horizontal').grid(row=18, column=0, sticky='ew', pady=10)
        ttk.Button(tool_frame, text="Save Design", command=self.save_design).grid(row=19, column=0, pady=5)
        ttk.Button(tool_frame, text="Load Design", command=self.load_design).grid(row=20, column=0, pady=5)
        ttk.Button(tool_frame, text="Load Image", command=self.load_image).grid(row=21, column=0, pady=5)
        ttk.Button(tool_frame, text="Export PNG", command=self.export_png).grid(row=22, column=0, pady=5)
        
        # Matrix control
        ttk.Separator(tool_frame, orient='horizontal').grid(row=23, column=0, sticky='ew', pady=10)
        ttk.Label(tool_frame, text="LED Matrix Control:").grid(row=24, column=0, pady=(5, 2))
        self.matrix_status = ttk.Label(tool_frame, text="Matrix: Disabled", foreground="red")
        self.matrix_status.grid(row=25, column=0, pady=2)
        self.matrix_btn = ttk.Button(tool_frame, text="Enable Matrix", command=self.toggle_matrix)
        self.matrix_btn.grid(row=26, column=0, pady=5)
        ttk.Button(tool_frame, text="Load to Panels", command=self.load_to_panels).grid(row=27, column=0, pady=5)
        
        # Canvas frame
        canvas_frame = ttk.LabelFrame(main_frame, text="Drawing Canvas - Two 64x64 Panels (128x64)", padding="10")
        canvas_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Drawing canvas container
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.pack()
        
        # Drawing canvas (128x64 for both panels)
        self.canvas = tk.Canvas(
            canvas_container,
            width=self.total_width * self.pixel_size,
            height=self.total_height * self.pixel_size,
            bg='black',
            cursor='crosshair'
        )
        self.canvas.pack()
        
        # Panel separator line
        separator_x = self.panel_width * self.pixel_size
        self.canvas.create_line(
            separator_x, 0, separator_x, self.total_height * self.pixel_size,
            fill='#333333', width=2, dash=(4, 4)
        )
        
        # Panel labels
        label_frame = ttk.Frame(canvas_container)
        label_frame.pack(pady=5)
        ttk.Label(label_frame, text="◄ Panel 1 (64x64) ►", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=20)
        ttk.Label(label_frame, text="◄ Panel 2 (64x64) ►", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=20)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-Shift-Z>', lambda e: self.redo())  # Alternative redo
        
        # Info panel
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.info_label = ttk.Label(info_frame, text="Ready to draw | Move mouse to draw")
        self.info_label.pack()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
    def initialize_matrix(self):
        """Initialize the RGB LED Matrix"""
        if not GPIO_AVAILABLE:
            self.info_label.config(text="GPIO not available - Running in simulation mode")
            return
            
        try:
            options = RGBMatrixOptions()
            # Configuration for two 64x64 panels (128x64 total display)
            options.rows = 64              # Each panel has 64 rows
            options.cols = 64              # Each panel has 64 columns
            options.chain_length = 2       # Two panels chained together
            options.parallel = 1           # Single chain
            options.hardware_mapping = 'regular'  # Change to 'adafruit-hat' if using Adafruit HAT
            options.gpio_slowdown = 4      # Adjust if flickering (1-4)
            options.brightness = 50        # Brightness 0-100
            options.disable_hardware_pulsing = True
            options.pwm_lsb_nanoseconds = 130  # Fine-tune PWM timing
            
            self.matrix = RGBMatrix(options=options)
            self.info_label.config(text="Matrix initialized successfully! (2x 64x64 panels)")
        except Exception as e:
            self.info_label.config(text=f"Matrix init failed: {str(e)}")
            messagebox.showwarning("Matrix Error", f"Could not initialize LED matrix: {str(e)}")
    
    def choose_color(self):
        """Open color picker dialog"""
        color = colorchooser.askcolor(initialcolor=self.current_color)
        if color[1]:
            self.set_color(color[1])
    
    def set_color(self, color):
        """Set the current drawing color"""
        self.current_color = color
        self.color_display.config(bg=color)
    
    def get_pixel_coords(self, event):
        """Convert canvas coordinates to pixel coordinates"""
        x = event.x // self.pixel_size
        y = event.y // self.pixel_size
        if 0 <= x < self.total_width and 0 <= y < self.total_height:
            panel = 1 if x < self.panel_width else 2
            return x, y, panel
        return None, None, None
    
    def start_draw(self, event):
        """Start drawing"""
        # Save state for undo before starting to draw
        self.save_state()
        self.drawing = True
        self.draw(event)
    
    def draw(self, event):
        """Draw pixel at mouse position with throttling"""
        if not self.drawing:
            return
        
        # Throttle drawing updates for better performance
        current_time = time.time()
        if current_time - self.last_draw_time < self.draw_throttle:
            return
        self.last_draw_time = current_time
            
        x, y, panel = self.get_pixel_coords(event)
        if x is not None:
            self.draw_pixel(x, y, self.current_color)
            panel_x = x if panel == 1 else x - self.panel_width
            self.info_label.config(text=f"Drawing at Panel {panel}: ({panel_x}, {y}) | Total: ({x}, {y})")
    
    def stop_draw(self, event):
        """Stop drawing"""
        self.drawing = False
    
    def draw_pixel(self, x, y, color):
        """Draw a single pixel on canvas and update pixel data"""
        # Update canvas
        x1 = x * self.pixel_size
        y1 = y * self.pixel_size
        x2 = x1 + self.pixel_size
        y2 = y1 + self.pixel_size
        
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
        
        # Update pixel data
        rgb = self.hex_to_rgb(color)
        self.pixel_data[y, x] = rgb
        
        # Update matrix if enabled
        if self.matrix_enabled and self.matrix:
            self.update_matrix_pixel(x, y, rgb)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def clear_canvas(self):
        """Clear the entire canvas"""
        self.save_state()  # Save for undo
        self.canvas.delete('all')
        self.pixel_data = np.zeros((self.total_height, self.total_width, 3), dtype=np.uint8)
        # Redraw separator line
        separator_x = self.panel_width * self.pixel_size
        self.canvas.create_line(
            separator_x, 0, separator_x, self.total_height * self.pixel_size,
            fill='#333333', width=2, dash=(4, 4)
        )
        if self.matrix_enabled:
            self.update_full_matrix()
        self.info_label.config(text="Both panels cleared")
    
    def fill_canvas(self):
        """Fill canvas with current color"""
        self.save_state()  # Save for undo
        rgb = self.hex_to_rgb(self.current_color)
        for y in range(self.total_height):
            for x in range(self.total_width):
                self.draw_pixel(x, y, self.current_color)
        self.info_label.config(text="Both panels filled")
    
    def save_state(self):
        """Save current state to undo stack"""
        # Save a copy of current pixel data
        state = self.pixel_data.copy()
        self.undo_stack.append(state)
        
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_levels:
            self.undo_stack.pop(0)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
    
    def undo(self):
        """Undo last action"""
        if not self.undo_stack:
            self.info_label.config(text="Nothing to undo")
            return
        
        # Save current state to redo stack
        self.redo_stack.append(self.pixel_data.copy())
        
        # Restore previous state
        self.pixel_data = self.undo_stack.pop()
        self.redraw_canvas()
        self.info_label.config(text=f"Undo - {len(self.undo_stack)} actions remaining")
    
    def redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            self.info_label.config(text="Nothing to redo")
            return
        
        # Save current state to undo stack
        self.undo_stack.append(self.pixel_data.copy())
        
        # Restore redo state
        self.pixel_data = self.redo_stack.pop()
        self.redraw_canvas()
        self.info_label.config(text=f"Redo - {len(self.redo_stack)} redos available")
    
    def save_design(self):
        """Save the current design to a JSON file"""
        import os
        # Use the actual user's home directory, not root's
        sudo_user = os.environ.get('SUDO_USER', 'tranas123')
        initial_dir = f"/home/{sudo_user}/Desktop/Lemona"
        
        if not os.path.exists(initial_dir):
            initial_dir = f"/home/{sudo_user}/Desktop"
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        filename = filedialog.asksaveasfilename(
            title="Save Design",
            initialdir=initial_dir,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            data = {
                'width': self.total_width,
                'height': self.total_height,
                'panels': 2,
                'pixels': self.pixel_data.tolist()
            }
            with open(filename, 'w') as f:
                json.dump(data, f)
            self.info_label.config(text=f"Saved both panels to {filename}")
            messagebox.showinfo("Success", "Design saved successfully!")
    
    def load_design(self):
        """Load a design from a JSON file"""
        import os
        # Use the actual user's home directory, not root's
        sudo_user = os.environ.get('SUDO_USER', 'tranas123')
        initial_dir = f"/home/{sudo_user}/Desktop/Lemona"
        
        if not os.path.exists(initial_dir):
            initial_dir = f"/home/{sudo_user}/Desktop"
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        filename = filedialog.askopenfilename(
            title="Load Design",
            initialdir=initial_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                loaded_data = np.array(data['pixels'], dtype=np.uint8)
                # Check if dimensions match
                if loaded_data.shape[0] == self.total_height and loaded_data.shape[1] == self.total_width:
                    self.pixel_data = loaded_data
                else:
                    # Try to fit the data
                    messagebox.showwarning("Size Mismatch", 
                        f"Loaded design size {loaded_data.shape[:2]} doesn't match canvas {(self.total_height, self.total_width)}")
                    return
                self.redraw_canvas()
                self.info_label.config(text=f"Loaded both panels from {filename}")
                messagebox.showinfo("Success", "Design loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load design: {str(e)}")
    
    def load_image(self):
        """Load an image file and convert it to the canvas"""
        import os
        # Use the actual user's home directory, not root's
        # First try to get the SUDO_USER environment variable
        sudo_user = os.environ.get('SUDO_USER', 'tranas123')
        initial_dir = f"/home/{sudo_user}/Desktop/Lemona"
        
        # Fallback options if the directory doesn't exist
        if not os.path.exists(initial_dir):
            initial_dir = f"/home/{sudo_user}/Desktop"
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()  # Use current working directory
        
        filename = filedialog.askopenfilename(
            title="Select an image file",
            initialdir=initial_dir,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            try:
                # Open the image
                img = Image.open(filename)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to fit the canvas (128x64)
                # Use LANCZOS for high-quality downsampling
                img_resized = img.resize((self.total_width, self.total_height), Image.Resampling.LANCZOS)
                
                # Convert to numpy array
                self.pixel_data = np.array(img_resized, dtype=np.uint8)
                
                # Redraw the canvas
                self.redraw_canvas()
                
                self.info_label.config(text=f"Image loaded from {filename}")
                messagebox.showinfo("Success", f"Image loaded and resized to {self.total_width}x{self.total_height}!")
                
            except PermissionError:
                error_msg = f"Permission denied: Cannot access {filename}\n\nTry running with sudo or check file permissions."
                self.info_label.config(text="Permission denied")
                messagebox.showerror("Permission Error", error_msg)
            except Exception as e:
                error_msg = f"Failed to load image: {str(e)}"
                self.info_label.config(text=error_msg)
                messagebox.showerror("Error", error_msg)
    
    def export_png(self):
        """Export the design as a PNG image"""
        import os
        # Use the actual user's home directory, not root's
        sudo_user = os.environ.get('SUDO_USER', 'tranas123')
        initial_dir = f"/home/{sudo_user}/Desktop/Lemona"
        
        if not os.path.exists(initial_dir):
            initial_dir = f"/home/{sudo_user}/Desktop"
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        filename = filedialog.asksaveasfilename(
            title="Export PNG",
            initialdir=initial_dir,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            try:
                img = Image.fromarray(self.pixel_data, 'RGB')
                img.save(filename)
                self.info_label.config(text=f"Exported both panels to {filename}")
                messagebox.showinfo("Success", "PNG exported successfully!")
            except PermissionError:
                error_msg = f"Permission denied: Cannot write to {filename}\n\nTry a different location or check permissions."
                self.info_label.config(text="Permission denied")
                messagebox.showerror("Permission Error", error_msg)
            except Exception as e:
                error_msg = f"Failed to export: {str(e)}"
                self.info_label.config(text=error_msg)
                messagebox.showerror("Error", error_msg)
    
    def redraw_canvas(self):
        """Redraw the entire canvas from pixel data"""
        self.canvas.delete('all')
        for y in range(self.total_height):
            for x in range(self.total_width):
                rgb = self.pixel_data[y, x]
                if not np.array_equal(rgb, [0, 0, 0]):
                    color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
                    x1 = x * self.pixel_size
                    y1 = y * self.pixel_size
                    x2 = x1 + self.pixel_size
                    y2 = y1 + self.pixel_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
        
        # Redraw separator line
        separator_x = self.panel_width * self.pixel_size
        self.canvas.create_line(
            separator_x, 0, separator_x, self.total_height * self.pixel_size,
            fill='#333333', width=2, dash=(4, 4)
        )
        
        if self.matrix_enabled:
            self.update_full_matrix()
    
    def toggle_matrix(self):
        """Toggle the LED matrix on/off"""
        if not GPIO_AVAILABLE or not self.matrix:
            messagebox.showwarning("Matrix Unavailable", 
                                 "LED Matrix hardware not available. Running in simulation mode.")
            return
        
        self.matrix_enabled = not self.matrix_enabled
        
        if self.matrix_enabled:
            self.matrix_status.config(text="Matrix: Enabled", foreground="green")
            self.matrix_btn.config(text="Disable Matrix")
            self.running = True
            self.update_full_matrix()
            self.info_label.config(text="LED Matrix enabled - Drawing updates in real-time")
        else:
            self.matrix_status.config(text="Matrix: Disabled", foreground="red")
            self.matrix_btn.config(text="Enable Matrix")
            self.running = False
            if self.matrix:
                self.matrix.Clear()
            self.info_label.config(text="LED Matrix disabled")
    
    def load_to_panels(self):
        """Load the current design to the LED matrix panels"""
        if not GPIO_AVAILABLE or not self.matrix:
            messagebox.showwarning("Matrix Unavailable", 
                                 "LED Matrix hardware not available. Running in simulation mode.")
            return
        
        try:
            self.info_label.config(text="Loading design to LED panels...")
            self.root.update()
            
            # Enable matrix if not already enabled
            if not self.matrix_enabled:
                self.matrix_enabled = True
                self.matrix_status.config(text="Matrix: Enabled", foreground="green")
                self.matrix_btn.config(text="Disable Matrix")
                self.running = True
            
            # Clear the matrix first
            self.matrix.Clear()
            
            # Load the entire pixel data to the matrix (both panels)
            for y in range(min(self.total_height, self.matrix.height)):
                for x in range(min(self.total_width, self.matrix.width)):
                    rgb = self.pixel_data[y, x]
                    self.matrix.SetPixel(x, y, int(rgb[0]), int(rgb[1]), int(rgb[2]))
            
            self.info_label.config(text="Design loaded to LED panels successfully!")
            messagebox.showinfo("Success", "Design loaded to LED matrix panels!")
            
        except Exception as e:
            error_msg = f"Failed to load to panels: {str(e)}"
            self.info_label.config(text=error_msg)
            messagebox.showerror("Load Error", error_msg)
    
    def update_matrix_pixel(self, x, y, rgb):
        """Update a single pixel on the LED matrix"""
        if self.matrix:
            try:
                self.matrix.SetPixel(x, y, rgb[0], rgb[1], rgb[2])
            except Exception as e:
                print(f"Error updating pixel: {e}")
    
    def update_full_matrix(self):
        """Update the entire LED matrix (both panels)"""
        if not self.matrix:
            return
            
        try:
            for y in range(min(self.total_height, self.matrix.height)):
                for x in range(min(self.total_width, self.matrix.width)):
                    rgb = self.pixel_data[y, x]
                    self.matrix.SetPixel(x, y, rgb[0], rgb[1], rgb[2])
        except Exception as e:
            print(f"Error updating matrix: {e}")
    
    def on_closing(self):
        """Cleanup when closing the application"""
        self.running = False
        if self.matrix:
            self.matrix.Clear()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = LEDMatrixDrawer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
