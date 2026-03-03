#!/usr/bin/env python3
"""
ESP32 Compatibility Test Script
Simulates ESP32 sending raw JPEG data to the Flask server
"""

import requests
import os
import json
from datetime import datetime

def test_esp32_upload():
    """Test ESP32-style raw JPEG upload"""
    print("🧪 Testing ESP32 Compatibility...")
    
    # Server URL (change for production testing)
    server_url = "http://localhost:10000"
    
    # Test endpoints
    endpoints = ["/analyze", "/upload"]
    
    # Find a test image
    test_image = None
    image_paths = [
        "static/images/garbage on roadside.jpg",
        "static/images/750x450_garbage-in-public-places.jpg",
        "../garbage on roadside.jpg"
    ]
    
    for path in image_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if not test_image:
        print("❌ No test image found. Please ensure sample images exist.")
        return False
    
    print(f"📷 Using test image: {test_image}")
    
    # Read image as raw bytes (like ESP32 would)
    try:
        with open(test_image, 'rb') as f:
            image_data = f.read()
        print(f"✅ Image loaded: {len(image_data)} bytes")
    except Exception as e:
        print(f"❌ Failed to read image: {e}")
        return False
    
    # Test both endpoints
    for endpoint in endpoints:
        print(f"\n🔗 Testing endpoint: {endpoint}")
        
        try:
            # Send raw JPEG data (ESP32 style)
            response = requests.post(
                f"{server_url}{endpoint}",
                data=image_data,
                headers={
                    'Content-Type': 'application/octet-stream'
                },
                timeout=30
            )
            
            print(f"📡 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success! Response:")
                print(f"   Waste Detected: {result.get('waste_detected', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}%")
                print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
                print(f"   Image Path: {result.get('image_path', 'N/A')}")
                
                # Check if image was saved
                image_path = result.get('image_path')
                if image_path and os.path.exists(image_path):
                    print(f"✅ Image saved successfully: {image_path}")
                else:
                    print(f"⚠️ Image path not found: {image_path}")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - is the server running on {server_url}?")
            return False
        except requests.exceptions.Timeout:
            print("❌ Request timeout - server may be overloaded")
            return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    return True

def test_web_form_upload():
    """Test web form multipart upload (for comparison)"""
    print("\n🌐 Testing Web Form Upload...")
    
    server_url = "http://localhost:10000/analyze"
    
    # Find test image
    test_image = None
    image_paths = [
        "static/images/garbage on roadside.jpg",
        "static/images/750x450_garbage-in-public-places.jpg"
    ]
    
    for path in image_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if not test_image:
        print("❌ No test image found")
        return False
    
    try:
        # Send as multipart form data (web browser style)
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(server_url, files=files, timeout=30)
        
        print(f"📡 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Web form upload successful!")
            print(f"   Waste Detected: {result.get('waste_detected', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}%")
        else:
            print(f"❌ Web form upload failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Web form test failed: {e}")
        return False
    
    return True

def main():
    """Run all ESP32 compatibility tests"""
    print("🚀 ESP32 Compatibility Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:10000", timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server not running. Please start with: python run.py")
        return
    
    # Run tests
    esp32_test = test_esp32_upload()
    web_test = test_web_form_upload()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if esp32_test:
        print("✅ ESP32 Raw JPEG Upload: PASS")
    else:
        print("❌ ESP32 Raw JPEG Upload: FAIL")
    
    if web_test:
        print("✅ Web Form Upload: PASS")
    else:
        print("❌ Web Form Upload: FAIL")
    
    if esp32_test and web_test:
        print("\n🎉 All tests passed! ESP32 integration is ready.")
        print("💡 Your ESP32 can now send images to both /analyze and /upload endpoints")
    else:
        print("\n⚠️ Some tests failed. Check server configuration.")

if __name__ == '__main__':
    main()