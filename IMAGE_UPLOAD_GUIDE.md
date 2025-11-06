# 📷 Image Upload Feature Guide

## ✅ New Feature Added!

You can now **upload images directly** to your LED matrix canvas!

---

## 🎨 How to Upload Images

### Step 1: Run the Application
```bash
sudo python3 led_matrix_drawer.py
```

### Step 2: Click "Load Image" Button
Look in the left toolbar under the Save/Load section:
- Save Design
- Load Design
- **Load Image** ← Click this!
- Export PNG

### Step 3: Select Your Image
- Supports: PNG, JPG, JPEG, GIF, BMP
- Image will automatically resize to 128x64 (both panels)
- Click "Open" to load

### Step 4: Display on LED Panels
- Your image appears on the canvas
- Click **"Load to Panels"** to display it on your LED matrix!

---

## 🔧 Fixing Permission Errors

### Error Message:
```
Permission denied: Cannot access [filename]
```

### Solution 1: Run with sudo
```bash
sudo python3 led_matrix_drawer.py
```

### Solution 2: Fix File Permissions
```bash
# Make the file readable
chmod +r your_image.png

# Or move image to your home directory
cp /path/to/image.png ~/Desktop/Lemona/
```

### Solution 3: Use Images in Your Home Directory
Store images in locations you have access to:
```bash
~/Desktop/
~/Pictures/
~/Documents/
~/Desktop/Lemona/
```

---

## 📁 Recommended Workflow

1. **Place images in the Lemona folder:**
   ```bash
   cp ~/Pictures/myimage.png ~/Desktop/Lemona/
   ```

2. **Run the application:**
   ```bash
   sudo python3 led_matrix_drawer.py
   ```

3. **Load your image:**
   - Click "Load Image"
   - Navigate to the Lemona folder
   - Select your image

4. **Display on LED matrix:**
   - Click "Load to Panels"

---

## 🖼️ Image Processing

### What Happens to Your Image:
1. **Conversion**: Converted to RGB (if not already)
2. **Resizing**: Automatically resized to **128x64** pixels
3. **Quality**: Uses high-quality LANCZOS resampling
4. **Fit**: Stretches to fill both panels

### Best Image Sizes:
- **Ideal**: 128x64 pixels (no resizing needed)
- **Good**: 256x128, 384x192 (2x, 3x multiples)
- **Okay**: Any size (will be resized)

### Tips:
- Wide images work best (2:1 aspect ratio)
- 128x64 images display perfectly
- Larger images are downsampled

---

## 🎯 Test Image Included

A test image has been created for you:
```
/home/tranas123/Desktop/Lemona/test_image.png
```

Try loading it:
1. Run: `sudo python3 led_matrix_drawer.py`
2. Click "Load Image"
3. Select `test_image.png`
4. Click "Load to Panels"

---

## 💡 Common Issues & Solutions

### Issue: "Permission denied" when loading
**Solution:**
```bash
# Run with sudo
sudo python3 led_matrix_drawer.py

# Or fix file permissions
chmod +r your_image.png
```

### Issue: "Permission denied" when saving
**Solution:**
```bash
# Save to your home directory
# Click "Export PNG" and choose:
~/Desktop/Lemona/output.png
```

### Issue: Image looks distorted
**Cause:** Original image aspect ratio differs from 2:1  
**Solution:** Pre-crop your image to 2:1 ratio before loading

### Issue: Colors look wrong
**Cause:** Image color space or LED brightness  
**Solution:** 
- Adjust LED brightness in code (line 106)
- Use brighter/higher contrast images

---

## 🔍 Supported Image Formats

| Format | Extension | Supported |
|--------|-----------|-----------|
| PNG | .png | ✓ Yes |
| JPEG | .jpg, .jpeg | ✓ Yes |
| GIF | .gif | ✓ Yes |
| BMP | .bmp | ✓ Yes |
| WebP | .webp | ✓ Yes (if Pillow supports) |

---

## 📊 Image Specifications

### Canvas Size
- **Width**: 128 pixels (both panels)
- **Height**: 64 pixels
- **Aspect Ratio**: 2:1
- **Color Depth**: 24-bit RGB

### LED Panel Mapping
```
┌────────────────┬────────────────┐
│                │                │
│  Panel 1       │  Panel 2      │
│  (Left 64px)   │  (Right 64px) │
│                │                │
└────────────────┴────────────────┘
   Your image spans both panels
```

---

## 🎨 Image Editing Tips

### Before Uploading:
1. **Resize** to 128x64 for best results
2. **Enhance contrast** for LED visibility
3. **Brighten** colors (LEDs work best with bright colors)
4. **Crop** to 2:1 aspect ratio

### Tools You Can Use:
- GIMP (free): `sudo apt install gimp`
- ImageMagick: `convert input.jpg -resize 128x64! output.png`
- Online tools: pixlr.com, photopea.com

### Quick Resize with Command Line:
```bash
# Install ImageMagick
sudo apt install imagemagick

# Resize any image to 128x64
convert your_image.jpg -resize 128x64! resized.png

# Load resized.png in the app
```

---

## 🚀 Quick Start Example

```bash
# 1. Copy your image to the Lemona folder
cp ~/Pictures/photo.jpg ~/Desktop/Lemona/

# 2. (Optional) Resize it
convert photo.jpg -resize 128x64! photo_resized.png

# 3. Run the app with sudo
sudo python3 led_matrix_drawer.py

# 4. In the GUI:
#    - Click "Load Image"
#    - Select photo_resized.png
#    - Click "Load to Panels"

# 5. Your image appears on the LED matrix!
```

---

## ✨ Feature Summary

| Feature | Description |
|---------|-------------|
| **Load Image** | Upload any image file |
| **Auto-resize** | Fits to 128x64 automatically |
| **Multiple formats** | PNG, JPG, GIF, BMP supported |
| **Permission handling** | Clear error messages |
| **High quality** | LANCZOS resampling |
| **Live preview** | See image before loading to panels |

---

## 🎯 Try It Now!

1. **Test with the included image:**
   ```bash
   sudo python3 led_matrix_drawer.py
   ```
   Then load `test_image.png`

2. **Use your own image:**
   - Copy image to Lemona folder
   - Load it via "Load Image" button
   - Display on panels!

---

**Now you can display photos, art, and designs on your LED matrix! 📷✨**
