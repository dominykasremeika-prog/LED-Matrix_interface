#!/bin/bash
# Complete test to verify image upload is working

echo "🧪 Testing Image Upload Fix"
echo "============================"
echo ""

# Test 1: Check permissions
echo "Test 1: Checking directory permissions..."
if [ "$(stat -c %a ~)" == "755" ]; then
    echo "  ✅ Home directory: 755 (correct)"
else
    echo "  ❌ Home directory: $(stat -c %a ~) (should be 755)"
    echo "     Run: ./fix-permissions.sh"
fi

if [ "$(stat -c %a ~/Desktop)" == "755" ]; then
    echo "  ✅ Desktop directory: 755 (correct)"
else
    echo "  ❌ Desktop directory: $(stat -c %a ~/Desktop) (should be 755)"
fi

if [ "$(stat -c %a ~/Desktop/Lemona)" == "755" ]; then
    echo "  ✅ Lemona directory: 755 (correct)"
else
    echo "  ❌ Lemona directory: $(stat -c %a ~/Desktop/Lemona) (should be 755)"
fi

# Test 2: Check sudo access
echo ""
echo "Test 2: Checking sudo can access directories..."
if sudo test -d ~/Desktop/Lemona; then
    echo "  ✅ Sudo can access Lemona directory"
else
    echo "  ❌ Sudo cannot access Lemona directory"
fi

# Test 3: Check test image
echo ""
echo "Test 3: Checking test image..."
if [ -f ~/Desktop/Lemona/test_image.png ]; then
    echo "  ✅ Test image exists"
    if [ "$(stat -c %a ~/Desktop/Lemona/test_image.png)" == "644" ]; then
        echo "  ✅ Test image permissions: 644 (correct)"
    else
        echo "  ⚠️  Test image permissions: $(stat -c %a ~/Desktop/Lemona/test_image.png) (recommended: 644)"
    fi
else
    echo "  ❌ Test image not found"
fi

# Test 4: Check sudo can read image
echo ""
echo "Test 4: Checking sudo can read test image..."
if sudo test -r ~/Desktop/Lemona/test_image.png; then
    echo "  ✅ Sudo can read test image"
else
    echo "  ❌ Sudo cannot read test image"
fi

# Test 5: Python image loading test
echo ""
echo "Test 5: Testing Python image loading..."
python3 test_image_load.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Python can load images (without sudo)"
else
    echo "  ❌ Python cannot load images"
fi

echo ""
echo "Test 6: Testing Python with sudo..."
sudo python3 test_image_load.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Python can load images (with sudo)"
else
    echo "  ❌ Python cannot load images with sudo"
fi

# Summary
echo ""
echo "========================================"
echo "📊 Test Summary"
echo "========================================"
echo ""
echo "If all tests passed above, you can now:"
echo "  1. Run: ./run.sh"
echo "  2. Click 'Load Image' button"
echo "  3. Select test_image.png"
echo "  4. Success! 🎉"
echo ""
echo "If any tests failed:"
echo "  1. Run: ./fix-permissions.sh"
echo "  2. Run this test again: ./test-everything.sh"
echo ""
