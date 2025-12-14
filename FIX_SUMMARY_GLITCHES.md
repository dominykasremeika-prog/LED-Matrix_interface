# Glitch Fix & Live Rotation Update

## Issues Addressed
1. **Glitches when opening settings**: Accessing the settings page triggered a hardware re-initialization (`init_matrix`), which conflicted with the active drawing loop, causing visual artifacts or crashes.
2. **Non-live Rotation**: Panel rotation required a full settings save or service restart to take effect visually.

## Changes Made
1. **Thread Safety (`threading.Lock`)**:
   - Added a `matrix_lock` to the `MatrixController` class.
   - Protected all hardware access (`init_matrix`, `_run_loop`, `_play_video`, `set_rotations`) with this lock.
   - This ensures that the matrix is never being re-initialized while it is being drawn to, and vice-versa.

2. **Optimized Initialization**:
   - `init_matrix` now checks if the hardware settings have *actually changed* before tearing down and re-creating the matrix object.
   - This prevents unnecessary flickering when just saving client-side settings (like brightness or rotation) or when the settings page is just loaded (if it triggered a check).

3. **Live Rotation**:
   - Updated `set_rotations` to force an immediate redraw of the current image using the new rotation values.
   - This happens instantly when the "Rotate" buttons are clicked, without needing to reload the entire matrix.

## Verification
- The service has been restarted with the new code.
- "Rotate Panel" buttons should now work instantly.
- Opening the Settings menu should no longer cause the display to glitch.
