#!/bin/bash

SERVICE_FILE="/etc/systemd/system/led-matrix.service"
APP_DIR=$(pwd)
USER="root"

echo "Creating systemd service..."

# Stop existing service if running
sudo systemctl stop led-matrix.service 2>/dev/null

# Create service file
cat <<EOF | sudo tee $SERVICE_FILE
[Unit]
Description=LED Matrix Web Interface
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/web_app.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting service..."
sudo systemctl enable led-matrix.service
sudo systemctl start led-matrix.service

echo "Service installed and started!"
echo "Check status with: sudo systemctl status led-matrix.service"
