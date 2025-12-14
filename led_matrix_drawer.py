#!/usr/bin/env python3
"""
LED Matrix Drawing Application - Web Server Mode
"""

import sys
import os

# Redirect to web app
print("Starting Web Interface...")
os.execv(sys.executable, [sys.executable, "web_app.py"] + sys.argv[1:])
