#!/usr/bin/env python3
"""
Test script to verify image loading functionality
"""

import os
from PIL import Image
import numpy as np

def test_image_load():
    """Test loading and resizing an image"""
    print("=== Image Load Test ===\n")
    
    # Check if test image exists
    test_image_path = "/home/tranas123/Desktop/Lemona/test_image.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found at: {test_image_path}")
        return False
    
    print(f"✓ Test image found: {test_image_path}")
    
    try:
        # Test opening the image
        img = Image.open(test_image_path)
        print(f"✓ Image opened successfully")
        print(f"  Original size: {img.size}")
        print(f"  Original mode: {img.mode}")
        
        # Test converting to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"✓ Converted to RGB mode")
        
        # Test resizing
        target_size = (128, 64)
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        print(f"✓ Image resized to: {img_resized.size}")
        
        # Test converting to numpy array
        pixel_data = np.array(img_resized, dtype=np.uint8)
        print(f"✓ Converted to numpy array")
        print(f"  Array shape: {pixel_data.shape}")
        print(f"  Data type: {pixel_data.dtype}")
        
        # Check pixel values
        print(f"\nSample pixel values:")
        print(f"  Top-left pixel: RGB{tuple(pixel_data[0, 0])}")
        print(f"  Top-right pixel: RGB{tuple(pixel_data[0, 127])}")
        print(f"  Bottom-left pixel: RGB{tuple(pixel_data[63, 0])}")
        print(f"  Bottom-right pixel: RGB{tuple(pixel_data[63, 127])}")
        
        print(f"\n✅ All tests passed! Image loading should work correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_file_permissions():
    """Test file permissions for the Lemona directory"""
    print("\n=== File Permissions Test ===\n")
    
    lemona_dir = "/home/tranas123/Desktop/Lemona"
    
    # Check directory access
    if os.path.exists(lemona_dir):
        print(f"✓ Directory exists: {lemona_dir}")
    else:
        print(f"❌ Directory not found: {lemona_dir}")
        return False
    
    # Check read permission
    if os.access(lemona_dir, os.R_OK):
        print(f"✓ Read access: OK")
    else:
        print(f"❌ Read access: DENIED")
        return False
    
    # Check write permission
    if os.access(lemona_dir, os.W_OK):
        print(f"✓ Write access: OK")
    else:
        print(f"⚠ Write access: DENIED (may need sudo for saving)")
    
    # Check execute permission (for directory listing)
    if os.access(lemona_dir, os.X_OK):
        print(f"✓ Execute access: OK")
    else:
        print(f"❌ Execute access: DENIED")
        return False
    
    # Check current working directory
    cwd = os.getcwd()
    print(f"\nCurrent working directory: {cwd}")
    
    # Check SUDO_USER environment variable
    sudo_user = os.environ.get('SUDO_USER', 'Not set')
    print(f"SUDO_USER environment variable: {sudo_user}")
    
    # Check actual user
    import pwd
    actual_user = pwd.getpwuid(os.getuid()).pw_name
    print(f"Current user: {actual_user}")
    
    print(f"\n✅ Permissions check complete!")
    return True

if __name__ == "__main__":
    print("LED Matrix Drawer - Image Load Test\n")
    print("=" * 50)
    
    # Run tests
    perm_result = test_file_permissions()
    img_result = test_image_load()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"  Permissions: {'✅ PASSED' if perm_result else '❌ FAILED'}")
    print(f"  Image Load:  {'✅ PASSED' if img_result else '❌ FAILED'}")
    
    if perm_result and img_result:
        print("\n🎉 All tests passed! You can now load images in the app.")
        print("\nTo load the test image:")
        print("  1. Run: sudo python3 led_matrix_drawer.py")
        print("  2. Click 'Load Image' button")
        print("  3. Select 'test_image.png'")
        print("  4. Click 'Load to Panels'")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
