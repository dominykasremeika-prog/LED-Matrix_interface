# 🎯 Quick Fix for Image Upload Error

## The Problem
You see: **"Cannot change to the directory - Permission denied"**

## The Solution (Choose One)

### ⭐ Option 1: Fix Permissions + Use Run Script (RECOMMENDED)
```bash
cd ~/Desktop/Lemona
./fix-permissions.sh
./run.sh
```
This fixes directory permissions and runs the app correctly!

### Option 2: Just Use the Run Script
```bash
cd ~/Desktop/Lemona
./run.sh
```
The run script now automatically fixes permissions!

### Option 3: Simulation Mode (No Sudo)
```bash
cd ~/Desktop/Lemona
./run.sh --no-hardware
```
Perfect for testing without LED hardware!

---

## ✅ Test It Now

```bash
# 1. Fix permissions (one time):
./fix-permissions.sh

# 2. Run the application:
./run.sh

# 3. Click "Load Image" button

# 4. Select test_image.png

# 5. Click "Load to Panels"
```

---

## 📚 More Help

- **Detailed Guide:** See `TROUBLESHOOTING_IMAGE_UPLOAD.md`
- **Image Upload Guide:** See `IMAGE_UPLOAD_GUIDE.md`

---

## 🎉 That's It!

The image upload should now work without errors!
