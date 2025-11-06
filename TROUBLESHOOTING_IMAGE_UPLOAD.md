# 🔧 Troubleshooting Image Upload Issues

## Problem: "Permission denied" or "Cannot change to directory" Error

### Issue Description
When clicking "Load Image" button, you see an error like:
```
Cannot change to the directory "/home/tranas123/Desktop/Lemona"
Permission denied.
```

---

## ✅ Solution 1: Use the Correct Command to Start

**The issue:** When running with `sudo`, the file dialog may not have proper access to user directories.

**Fix:** Use the `-E` flag with sudo to preserve environment variables:

```bash
sudo -E python3 led_matrix_drawer.py
```

Or use the updated start script:
```bash
./start.sh
```

---

## ✅ Solution 2: Allow X11 Access for Root

**The issue:** Tkinter file dialogs need X11 display access when running with sudo.

**Fix:** Before running with sudo, allow X11 access:

```bash
# Allow root to access your X11 display
xhost +local:root

# Now run the application
sudo python3 led_matrix_drawer.py

# After closing, you can revoke access (optional)
xhost -local:root
```

**Or combine it in one command:**
```bash
xhost +local:root && sudo python3 led_matrix_drawer.py; xhost -local:root
```

---

## ✅ Solution 3: Run Without Sudo (Simulation Mode)

**If you don't need the LED matrix hardware right now:**

```bash
# Just run without sudo
python3 led_matrix_drawer.py
```

This will:
- ✓ Work perfectly for designing and testing
- ✓ Load images without permission issues
- ✓ Save/export your designs
- ✗ Won't display on physical LED matrix (simulation mode)

---

## ✅ Solution 4: Place Images in Accessible Location

**Make sure your image files are readable:**

```bash
# Check file permissions
ls -l ~/Desktop/Lemona/test_image.png

# If needed, make it readable
chmod 644 ~/Desktop/Lemona/test_image.png

# Or copy images to the Lemona directory
cp ~/Pictures/myimage.jpg ~/Desktop/Lemona/
```

---

## ✅ Solution 5: Use the Fixed Code

The code has been updated to automatically detect the correct user directory even when running with sudo. Make sure you're using the latest version:

```bash
# Check if the file has the fix
grep -n "SUDO_USER" led_matrix_drawer.py

# You should see lines with:
# sudo_user = os.environ.get('SUDO_USER', 'tranas123')
```

---

## 🧪 Test the Fix

Run the test script to verify everything works:

```bash
# Test without sudo
python3 test_image_load.py

# Test with sudo
sudo python3 test_image_load.py
```

Both should pass all tests!

---

## 📋 Quick Checklist

Before loading images, verify:

- [ ] Running from the correct directory: `/home/tranas123/Desktop/Lemona`
- [ ] Image file exists and is readable: `ls -l test_image.png`
- [ ] If using sudo, X11 access is granted: `xhost +local:root`
- [ ] Using the updated code with SUDO_USER detection
- [ ] File dialog opens to the correct directory

---

## 🎯 Recommended Workflow

**For Best Results:**

1. **Allow X11 access** (one time per session):
   ```bash
   xhost +local:root
   ```

2. **Navigate to the directory**:
   ```bash
   cd ~/Desktop/Lemona
   ```

3. **Run with sudo -E**:
   ```bash
   sudo -E python3 led_matrix_drawer.py
   ```

4. **Load your image**:
   - Click "Load Image"
   - Navigate if needed (should start in Lemona folder)
   - Select your image
   - Click Open

5. **Display on LED matrix**:
   - Click "Load to Panels"

---

## 🔍 Still Having Issues?

### Check the Environment Variables:

```bash
# When running with sudo, these should be set:
sudo python3 -c "import os; print('SUDO_USER:', os.environ.get('SUDO_USER')); print('PWD:', os.environ.get('PWD'))"
```

Should output:
```
SUDO_USER: tranas123
PWD: /home/tranas123/Desktop/Lemona
```

### Check X11 Display:

```bash
# Check if DISPLAY is set
echo $DISPLAY

# Should show something like:
:0
or
:1
```

### Check File Dialog Access:

Run this quick test:
```bash
sudo python3 -c "
import tkinter as tk
from tkinter import filedialog
import os

root = tk.Tk()
root.withdraw()

sudo_user = os.environ.get('SUDO_USER', 'tranas123')
initial_dir = f'/home/{sudo_user}/Desktop/Lemona'

print(f'Testing file dialog with initial_dir: {initial_dir}')
print(f'Directory exists: {os.path.exists(initial_dir)}')
print(f'Can read: {os.access(initial_dir, os.R_OK)}')

filename = filedialog.askopenfilename(initialdir=initial_dir)
print(f'Selected: {filename}')
"
```

---

## 💡 Alternative: Use Direct File Path

If the file dialog continues to have issues, you can modify the code to load a specific image directly:

```python
# Add this temporary function to your code:
def load_test_image_directly(self):
    """Load test image directly without file dialog"""
    filename = "/home/tranas123/Desktop/Lemona/test_image.png"
    try:
        img = Image.open(filename)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_resized = img.resize((self.total_width, self.total_height), Image.Resampling.LANCZOS)
        self.pixel_data = np.array(img_resized, dtype=np.uint8)
        self.redraw_canvas()
        self.info_label.config(text=f"Image loaded from {filename}")
        messagebox.showinfo("Success", "Test image loaded!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load: {str(e)}")
```

---

## ✅ Success Criteria

You'll know it's working when:

1. ✓ File dialog opens without errors
2. ✓ File dialog shows the Lemona directory
3. ✓ You can navigate and select files
4. ✓ Image loads and displays on canvas
5. ✓ "Load to Panels" shows image on LED matrix

---

## 🆘 Get More Help

If you're still stuck, provide these details:

1. **Command used to start:**
   ```bash
   # What command did you use?
   ```

2. **Error message:**
   ```
   # Copy the exact error
   ```

3. **Environment info:**
   ```bash
   whoami
   pwd
   echo $DISPLAY
   ls -la ~/Desktop/Lemona/test_image.png
   ```

4. **Test results:**
   ```bash
   python3 test_image_load.py
   ```

---

## 📝 Summary

**Most Common Solution:**
```bash
# One-time setup per session
xhost +local:root

# Run the application
cd ~/Desktop/Lemona
sudo -E python3 led_matrix_drawer.py
```

**That's it! You should now be able to load images successfully.** 🎉
