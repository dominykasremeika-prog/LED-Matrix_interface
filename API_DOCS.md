# API Endpoint Documentation

This document describes the API endpoints used by the LED Matrix Client to communicate with the server.

## Telemetry Endpoint

The client sends telemetry data to the server to report its status.

**Endpoint:** `POST /api/telemetry`

**Description:** Receives status updates from the LED Matrix client.

**Request Body (JSON):**

```json
{
  "polling_rate": 1.0,
  "gpio_slowdown": 4,
  "network": {
    "type": "WiFi",
    "ssid": "MyWiFiNetwork",
    "ip": "192.168.1.105"
  },
  "refresh_rate": 60,
  "hardware_pulsing": true,
  "brightness": 50,
  "screen_orientation": 0,
  "request_send_rate": 1.0
}
```

**Fields:**

*   `polling_rate` (float): The rate at which the client polls for new images (in Hz).
*   `gpio_slowdown` (int): The GPIO slowdown setting used by the matrix library.
*   `network` (object): Network connection details.
    *   `type` (string): "WiFi" or "Ethernet".
    *   `ssid` (string): The SSID of the connected WiFi network (if applicable).
    *   `ip` (string): The IP address of the client.
*   `refresh_rate` (int): The estimated refresh rate of the LED matrix (in Hz).
*   `hardware_pulsing` (boolean): Whether hardware pulsing is enabled (true) or disabled (false).
*   `brightness` (int): The current brightness setting (0-100).
*   `screen_orientation` (int): The rotation of the screen in degrees (0, 90, 180, 270).
*   `request_send_rate` (float): The actual rate at which requests are being sent (in Hz).

**Response:**

*   `200 OK`: Telemetry received successfully.

## Image Endpoints

The client fetches images from these endpoints to display on the matrix.

**Endpoint:** `GET /api/matrix/a`
**Description:** Returns the image for the first panel (left).

**Endpoint:** `GET /api/matrix/b`
**Description:** Returns the image for the second panel (right).
