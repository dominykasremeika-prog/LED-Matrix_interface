#!/usr/bin/env python3
"""
Test script to verify API connection and data format
"""

import requests
import json

API_URL = "http://45.80.148.216:8000/api/display"

print("=" * 60)
print("Testing API Connection")
print("=" * 60)
print(f"Endpoint: {API_URL}\n")

try:
    response = requests.get(API_URL, timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Successfully connected to API!")
        print(f"\nResponse structure:")
        print(f"- Keys: {list(data.keys())}")
        print(f"- Last updated: {data.get('last_updated')}")
        
        matrix_a = data.get('matrixA')
        matrix_b = data.get('matrixB')
        
        if matrix_a and matrix_b:
            print(f"\n✅ Matrix data found:")
            print(f"- Matrix A dimensions: {len(matrix_a)}x{len(matrix_a[0]) if matrix_a else 0}")
            print(f"- Matrix B dimensions: {len(matrix_b)}x{len(matrix_b[0]) if matrix_b else 0}")
            
            # Sample first pixel
            if len(matrix_a) > 0 and len(matrix_a[0]) > 0:
                print(f"- Sample pixel (0,0) Matrix A: {matrix_a[0][0]}")
                print(f"- Sample pixel (0,0) Matrix B: {matrix_b[0][0]}")
            
            # Check for non-black pixels
            non_black_count = 0
            for y in range(min(64, len(matrix_a))):
                for x in range(min(64, len(matrix_a[0]))):
                    if matrix_a[y][x] != [0, 0, 0]:
                        non_black_count += 1
            
            print(f"\n📊 Matrix A has {non_black_count} non-black pixels")
            
            if non_black_count == 0:
                print("\n⚠️  WARNING: All pixels are black! Try drawing something in the web interface.")
            else:
                print("\n✅ Matrix has content!")
                
        else:
            print("\n❌ Matrix data is missing or invalid")
    else:
        print(f"\n❌ API returned error code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n❌ Connection timeout - server might be down or unreachable")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection error: {e}")
    print("\nPossible issues:")
    print("- Server is not running")
    print("- Firewall blocking the connection")
    print("- Wrong IP address or port")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
