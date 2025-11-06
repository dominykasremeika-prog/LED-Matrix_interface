#!/bin/bash
# Fix permissions for image upload access

echo "🔧 Fixing Permissions for Image Upload"
echo "======================================="
echo ""

# Fix home directory permissions
echo "📁 Setting directory permissions..."
chmod 755 ~ 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Home directory: /home/$(whoami)"
else
    echo "  ✗ Could not modify home directory"
fi

chmod 755 ~/Desktop 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Desktop directory"
else
    echo "  ✗ Could not modify Desktop directory"
fi

chmod 755 ~/Desktop/Lemona 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Lemona directory"
else
    echo "  ✗ Could not modify Lemona directory"
fi

# Fix image file permissions
echo ""
echo "🖼️  Setting image file permissions..."
found_images=false

for ext in png jpg jpeg gif bmp PNG JPG JPEG GIF BMP; do
    if ls ~/Desktop/Lemona/*.$ext 1> /dev/null 2>&1; then
        chmod 644 ~/Desktop/Lemona/*.$ext 2>/dev/null
        count=$(ls ~/Desktop/Lemona/*.$ext 2>/dev/null | wc -l)
        echo "  ✓ Fixed $count .$ext file(s)"
        found_images=true
    fi
done

if [ "$found_images" = false ]; then
    echo "  ℹ No image files found in Lemona directory"
fi

# Verify permissions
echo ""
echo "🔍 Verifying permissions..."
echo ""

# Check directories
ls -ld ~ ~/Desktop ~/Desktop/Lemona 2>/dev/null | while read -r line; do
    echo "  $line"
done

# Check test image if it exists
if [ -f ~/Desktop/Lemona/test_image.png ]; then
    echo ""
    echo "📷 Test image:"
    ls -l ~/Desktop/Lemona/test_image.png
fi

echo ""
echo "✅ Permission fix complete!"
echo ""
echo "Now run the application with:"
echo "  ./run.sh"
