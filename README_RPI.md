# Raspberry Pi LED Matrix Controller

This program connects to your Lemona web interface and displays content on dual 64x64 LED matrices connected to a Raspberry Pi 4.

## Hardware Setup

### Requirements
- Raspberry Pi 4
- 2x 64x64 RGB LED Matrix panels
- RGB Matrix HAT (Adafruit HAT or equivalent)
- 5V power supply (adequate amperage for both panels - typically 15-20A)

### Wiring
1. **First panel (Matrix A)**: Connected to RPi4 via HAT on Panel1 port
2. **Second panel (Matrix B)**: Daisy-chained from Matrix A output

The panels are daisy-chained, appearing as a single 128x64 display to the RPi.

## Software Installation

### 1. Clone this repository
```bash
cd ~
git clone https://github.com/dominykasremeika-prog/Lemona.git
cd Lemona
```

### 2. Run installation script
```bash
chmod +x install_rpi.sh
./install_rpi.sh
```

This installs:
- rpi-rgb-led-matrix library
- Python dependencies
- Build tools

### 3. Configure API endpoint
Edit `rpi_led_controller.py` and set your server address:

```python
API_URL = "http://YOUR_SERVER_IP:8000/api/display"
```

Replace `YOUR_SERVER_IP` with:
- Your server's IP address if on local network
- Your domain name if deployed online

## Running the Controller

### Manual start
```bash
sudo python3 rpi_led_controller.py
```

**Note**: Must run with `sudo` for GPIO access.

### Run on boot (systemd service)

1. Create service file:
```bash
sudo nano /etc/systemd/system/led-matrix.service
```

2. Add this content:
```ini
[Unit]
Description=LED Matrix Controller
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/Lemona
ExecStart=/usr/bin/python3 /home/pi/Lemona/rpi_led_controller.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable led-matrix.service
sudo systemctl start led-matrix.service
```

4. Check status:
```bash
sudo systemctl status led-matrix.service
```

5. View logs:
```bash
sudo journalctl -u led-matrix.service -f
```

## Configuration Options

### Matrix Hardware Settings
Edit `rpi_led_controller.py` to adjust:

```python
# Panel configuration
options.rows = 64              # Rows per panel
options.cols = 64              # Columns per panel
options.chain_length = 2       # Number of daisy-chained panels
options.hardware_mapping = 'adafruit-hat'  # HAT type

# Performance tuning
options.gpio_slowdown = 2      # 1-4, increase if flickering
options.brightness = 50        # 0-100
options.pwm_bits = 11          # PWM precision (1-11)
```

### Polling Settings
```python
POLL_INTERVAL = 0.1  # Check API every 100ms (adjust for performance)
```

## Troubleshooting

### No display output
- Check power supply (LEDs need significant current)
- Verify GPIO connections
- Try different `gpio_slowdown` values (2-4)
- Check hardware_mapping setting matches your HAT

### Flickering
- Increase `gpio_slowdown` to 3 or 4
- Disable audio: add `dtparam=audio=off` to `/boot/config.txt`
- Check power supply quality

### Connection errors
- Verify API_URL is correct
- Check network connectivity: `ping YOUR_SERVER_IP`
- Ensure web server is running
- Check firewall rules

### Permission denied
- Always run with `sudo` for GPIO access
- If using systemd service, ensure `User=root`

## Hardware Mapping Options

Common hardware mappings:
- `adafruit-hat` - Adafruit RGB Matrix HAT/Bonnet
- `adafruit-hat-pwm` - Adafruit HAT with hardware PWM
- `regular` - Standard wiring
- `regular-pi1` - Original Raspberry Pi

## Performance Tips

1. **Reduce load**: Increase `POLL_INTERVAL` if RPi is struggling
2. **Disable desktop**: Use Raspberry Pi OS Lite (no GUI)
3. **Overclock**: Safely overclock RPi4 for better performance
4. **Quality power**: Use adequate 5V power supply
5. **Cooling**: Add heatsinks or fan if panels get warm

## API Communication

The controller polls this endpoint:
```
GET http://YOUR_SERVER:8000/api/display
```

Expected response format:
```json
{
  "matrixA": [[[ r, g, b ], ...], ...],  // 64x64 RGB array
  "matrixB": [[[ r, g, b ], ...], ...],  // 64x64 RGB array
  "last_updated": "2025-11-07T12:34:56.789"
}
```

## Stopping the Controller

### If running manually
Press `Ctrl+C`

### If running as service
```bash
sudo systemctl stop led-matrix.service
```

### Disable autostart
```bash
sudo systemctl disable led-matrix.service
```

## Support

For issues with:
- **Web interface**: See main Lemona README.md
- **LED matrix library**: https://github.com/hzeller/rpi-rgb-led-matrix
- **Hardware wiring**: Refer to your HAT documentation

---

**Note**: This controller is designed for the Lemona LED Matrix web interface. Both systems must be on the same network or the Lemona server must be accessible via internet.
