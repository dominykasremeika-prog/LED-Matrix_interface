# New Features & Updates

## Mirror Functionality
- Added "Mirror Panel" buttons to the UI next to the Rotate buttons.
- Implemented backend logic to flip panel content horizontally.
- Mirror state is saved in `settings.json` and persists across restarts.
- Mirroring updates live instantly.

## Enhanced Settings
- Added new hardware configuration options to the Settings menu:
  - **Scan Mode**: Progressive vs Interlaced.
  - **Multiplexing**: For panels with different multiplexing.
  - **Row Address Type**: For different addressing schemes.
  - **PWM Bits**: To adjust color depth vs refresh rate.
  - **Limit Refresh Rate**: To cap the refresh rate if needed.
- Moved the "Warning" alert to the top of the settings modal for better visibility.

## Restart Server
- The "Restart Server" button now restarts the `led-matrix.service` systemd service.
- This ensures a full hardware re-initialization, which is useful if the matrix gets into a bad state.

## Live Updates
- Both Rotation and Mirroring now update the display immediately upon clicking the button, without needing to save settings or restart.
