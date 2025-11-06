# 📦 Git Setup and Push Guide

Complete guide to set up Git and push your Lemona project to GitHub.

---

## 🎯 Quick Guide

```bash
# 1. Initialize git repository
cd ~/Desktop/Lemona
git init

# 2. Add all files
git add .

# 3. Create first commit
git commit -m "Initial commit: LED Matrix Drawing Application"

# 4. Create GitHub repository (do this on github.com first)

# 5. Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/Lemona.git

# 6. Push to GitHub
git push -u origin main
```

---

## 📋 Detailed Step-by-Step Guide

### Step 1: Install Git (if not installed)

```bash
# Check if git is installed
git --version

# If not installed:
sudo apt-get update
sudo apt-get install git -y
```

### Step 2: Configure Git

Set up your git identity (first time only):

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email (use your GitHub email)
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

### Step 3: Initialize Git Repository

Navigate to your project and initialize:

```bash
# Go to project directory
cd ~/Desktop/Lemona

# Initialize git repository
git init

# Check status
git status
```

### Step 4: Create .gitignore File

Create a `.gitignore` file to exclude unnecessary files:

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
test_output/
temp/

# Keep test image
!test_image.png
EOF
```

### Step 5: Add Files to Git

```bash
# Add all files
git add .

# Or add specific files
git add led_matrix_drawer.py
git add requirements.txt
git add README.md
git add SETUP.md
git add *.sh
git add *.md

# Check what will be committed
git status
```

### Step 6: Create First Commit

```bash
# Commit with a message
git commit -m "Initial commit: LED Matrix Drawing Application with undo/redo support"

# Verify commit
git log
```

### Step 7: Create GitHub Repository

1. **Go to GitHub.com** and log in
2. **Click the "+" icon** in the top right
3. **Select "New repository"**
4. **Fill in repository details:**
   - **Repository name:** `Lemona` (or your preferred name)
   - **Description:** `LED Matrix Drawing Application for Raspberry Pi`
   - **Visibility:** Public or Private
   - **DO NOT** initialize with README (you already have one)
5. **Click "Create repository"**

### Step 8: Connect to GitHub

```bash
# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Lemona.git

# Verify remote
git remote -v
```

### Step 9: Push to GitHub

```bash
# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**If prompted for credentials:**
- **Username:** Your GitHub username
- **Password:** Use a Personal Access Token (not your password!)

### Step 10: Create GitHub Personal Access Token

If you need a token:

1. Go to **GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **"Generate new token"**
3. Give it a name: `Lemona-Project`
4. Select scopes: Check **"repo"** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

### Step 11: Verify Upload

1. Go to your GitHub repository URL
2. Refresh the page
3. You should see all your files!

---

## 🔄 Making Updates

After making changes to your code:

```bash
# Check what changed
git status

# See detailed changes
git diff

# Add changed files
git add .

# Commit with descriptive message
git commit -m "Add undo/redo functionality and improve drawing performance"

# Push to GitHub
git push
```

---

## 📝 Good Commit Messages

Follow these patterns:

```bash
# Initial upload
git commit -m "Initial commit: LED Matrix Drawing Application"

# Adding features
git commit -m "Add undo/redo functionality with Ctrl+Z/Ctrl+Y support"
git commit -m "Add image import feature for PNG/JPG/GIF/BMP files"

# Fixing bugs
git commit -m "Fix permission denied error on image upload"
git commit -m "Fix drawing throttle for better performance"

# Updating documentation
git commit -m "Update README with new features and setup instructions"
git commit -m "Add comprehensive SETUP.md guide"

# Improvements
git commit -m "Optimize drawing performance with throttling"
git commit -m "Lower polling rate from 120fps to 60fps"
```

---

## 🌿 Working with Branches (Optional)

For more advanced workflows:

```bash
# Create a new branch for features
git checkout -b feature/new-tool

# Make changes and commit
git add .
git commit -m "Add new drawing tool"

# Push branch to GitHub
git push -u origin feature/new-tool

# Switch back to main branch
git checkout main

# Merge feature branch
git merge feature/new-tool

# Push updated main
git push
```

---

## 📦 Complete Upload Example

Here's a complete example workflow:

```bash
# Navigate to project
cd ~/Desktop/Lemona

# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.vscode/
.idea/
*.log
EOF

# Add all files
git add .

# Commit
git commit -m "Initial commit: LED Matrix Drawer with undo/redo and image import"

# Configure git (if first time)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/Lemona.git

# Rename to main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## 🔐 SSH Authentication (Alternative to HTTPS)

For easier authentication without tokens:

### Setup SSH Key

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your@email.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

### Add to GitHub

1. Go to **GitHub → Settings → SSH and GPG keys**
2. Click **"New SSH key"**
3. Paste your public key
4. Click **"Add SSH key"**

### Use SSH URL

```bash
# Remove HTTPS remote
git remote remove origin

# Add SSH remote
git remote add origin git@github.com:YOUR_USERNAME/Lemona.git

# Push
git push -u origin main
```

---

## 📊 Checking Repository Status

```bash
# Check current status
git status

# View commit history
git log
git log --oneline
git log --graph --oneline --all

# View changes
git diff

# View remote URL
git remote -v

# View branches
git branch -a
```

---

## 🔄 Pulling Updates

If you work on multiple computers:

```bash
# Pull latest changes
git pull origin main

# Or fetch and merge separately
git fetch origin
git merge origin/main
```

---

## 🆘 Common Issues

### Issue: "fatal: remote origin already exists"

```bash
# Remove existing remote
git remote remove origin

# Add again
git remote add origin https://github.com/YOUR_USERNAME/Lemona.git
```

### Issue: "Support for password authentication was removed"

**Solution:** Use a Personal Access Token instead of your password, or set up SSH authentication (see above).

### Issue: "failed to push some refs"

```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### Issue: Accidentally committed wrong files

```bash
# Unstage files (before commit)
git reset HEAD filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

---

## 📋 Repository Description Template

When creating your GitHub repository, use this description:

```
LED Matrix Drawing Application for Raspberry Pi

🎨 Features:
- Freehand pixel art drawing
- Undo/Redo support (Ctrl+Z/Ctrl+Y)
- Image import (PNG/JPG/GIF/BMP)
- Real-time LED matrix display
- Save/load designs
- Simulation mode

Built with Python, Tkinter, and rpi-rgb-led-matrix library.
```

---

## 🏷️ Adding a README Badge (Optional)

Add this to the top of your README.md:

```markdown
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
```

---

## ✅ Verification Checklist

Before pushing, verify:

- [ ] All files are added (`git status` shows clean)
- [ ] .gitignore excludes unnecessary files
- [ ] README.md is complete and accurate
- [ ] requirements.txt is up to date
- [ ] SETUP.md has installation instructions
- [ ] Commit message is descriptive
- [ ] GitHub repository is created
- [ ] Remote URL is correct
- [ ] Ready to push!

---

## 🎉 Success!

Your project is now on GitHub! Share the URL:

```
https://github.com/YOUR_USERNAME/Lemona
```

Anyone can now:
- View your code
- Clone your repository
- Report issues
- Contribute to your project

---

## 📚 Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

**Ready to push? Let's go!** 🚀

```bash
cd ~/Desktop/Lemona
git init
git add .
git commit -m "Initial commit: LED Matrix Drawing Application"
git remote add origin https://github.com/YOUR_USERNAME/Lemona.git
git push -u origin main
```
