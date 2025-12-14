# Slideshow and UI Updates

## Changes Made

1.  **Slideshow Logic**:
    -   Moved "Slide Duration" setting from the global Settings tab to the SD Card tab.
    -   Updated the slideshow logic to respect the duration set in the UI.
    -   Videos and GIFs now loop for the specified duration before moving to the next file (previously they played once).

2.  **Mobile UI Improvements**:
    -   Fixed layout issues where icons/text would overflow borders on small screens (added wrapping and overflow handling).
    -   Added a "Fullscreen" button to the Draw tab to make drawing easier on mobile devices.

3.  **Code Changes**:
    -   `web/templates/index.html`: Updated HTML structure, added CSS for mobile/fullscreen, updated JS to handle new slideshow logic.
    -   `web_app.py`: Updated `play_slideshow` route to accept duration. Updated `_play_video` to support a duration limit. Updated `_run_slideshow_step` to enforce the duration.

## How to Use

-   **Slideshow**: Go to the SD Card tab, enter the desired duration in seconds (default 10s), and click "Start Slideshow".
-   **Drawing**: Go to the Draw tab and click "Fullscreen" to open a distraction-free drawing interface.
