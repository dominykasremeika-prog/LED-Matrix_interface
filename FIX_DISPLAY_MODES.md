# Display Modes Fix and Implementation

## Changes Made

1.  **Configuration Fix**:
    -   Reverted `pwm_bits` to 11 in `settings.json` to prevent crashes/instability.
    -   Ensured `parallel` is set to 1.

2.  **Display Modes Implementation**:
    -   Updated `web_app.py` to fully support `split`, `clone`, `matrix_a`, and `matrix_b` modes for both Images and Videos.
    -   **Images**: `set_image` now resizes and composes the image onto the 128x64 canvas based on the selected mode.
        -   `split`: Resizes to 128x64 (fills both panels).
        -   `clone`: Resizes to 64x64 and duplicates on both panels.
        -   `matrix_a`: Resizes to 64x64 and places on the left panel.
        -   `matrix_b`: Resizes to 64x64 and places on the right panel.
    -   **Videos**: `_play_video` now performs real-time resizing and composition for MP4 and GIF frames based on the mode.
    -   **Architecture**:
        -   Updated `MatrixController` to store `current_video_mode`.
        -   Updated `set_video` to accept and store the mode.
        -   Updated `_run_loop` to pass the mode to the video player.
        -   Updated `_safe_set_image` signature to accept `mode` (preventing TypeErrors).

## How to Use

-   **Upload**: When uploading a file, select the desired mode (Split, Clone, Matrix A, Matrix B).
-   **SD Card**: When playing a file from SD card, the selected mode will be applied.

## Technical Details

-   The logic for "Clone" and "Matrix A/B" assumes a target resolution of 64x64 per panel.
-   The logic for "Split" assumes a target resolution of 128x64 (spanning both panels).
-   Image processing uses `LANCZOS` resampling for high quality.
