# Optimization Summary

## Performance Improvements
1.  **Removed Manual Pixel Loop**: Replaced the slow Python loop `SetPixel(x, y, r, g, b)` with the optimized C++ binding `canvas.SetImage(image)`. This is the single biggest performance boost, making image rendering orders of magnitude faster.
2.  **Static Image Caching**: The main run loop no longer re-renders static images 60 times a second. It now draws the image once when set (or when settings change) and then sleeps, freeing up CPU resources.
3.  **Efficient Redraws**: `set_image`, `set_rotations`, and `set_mirrors` now trigger an immediate single-frame update, ensuring responsiveness without the overhead of a continuous render loop.

## Bloat Removal
- Removed unnecessary debug prints.
- Simplified the `_run_loop` logic for the "image" mode.

## Notes
- Video playback still processes frames on the fly, but since `_safe_set_image` is now much faster (using `SetImage`), video playback smoothness should be significantly improved.
- The system is now much more efficient and should run cooler and more reliably.
