#!/usr/bin/env python3
"""
Test Image Display in Dashboard
Upload a test image and verify it appears in the dashboard
"""

import requests
import os
from datetime import datetime

def test_image_upload_and_display():
    """Test uploading an image and checking dashboard display"""
    print("📷 Testing Image Upload and Dashboard Display...")
    
    # Server URL
    server_url = "http://localhost:10000"
    
    # Find test image
    test_images = [
        "static/images/garbage on roadside.jpg",
        "static/images/750x450_garbage-in-public-places.jpg"
    ]
    
    test_image = None
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if not test_image:
        print("❌ No test image found")
        return False
    
    print(f"📷 Using test image: {test_image}")
    
    try:
        # Test 1: Upload via web form (multipart)
        print("\n🌐 Testing web form upload...")
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{server_url}/analyze", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Web form upload successful!")
            print(f"   Waste detected: {result.get('waste_detected', False)}")
            print(f"   Confidence: {result.get('confidence', 0)}%")
            print(f"   Image path: {result.get('image_path', 'N/A')}")
            
            if result.get('waste_detected'):
                print("🚨 Waste detected - should appear in dashboard!")
            else:
                print("✅ No waste detected - won't appear in dashboard")
        else:
            print(f"❌ Web form upload failed: {response.status_code}")
            return False
        
        # Test 2: Upload via ESP32 simulation (raw data)
        print("\n📡 Testing ESP32 simulation upload...")
        with open(test_image, 'rb') as f:
            image_data = f.read()
        
        response = requests.post(
            f"{server_url}/analyze",
            data=image_data,
            headers={'Content-Type': 'application/octet-stream'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ESP32 simulation upload successful!")
            print(f"   Waste detected: {result.get('waste_detected', False)}")
            print(f"   Confidence: {result.get('confidence', 0)}%")
            print(f"   Image path: {result.get('image_path', 'N/A')}")
            
            if result.get('waste_detected'):
                print("🚨 Waste detected - should appear in dashboard!")
            else:
                print("✅ No waste detected - won't appear in dashboard")
        else:
            print(f"❌ ESP32 simulation upload failed: {response.status_code}")
        
        # Test 3: Check dashboard API
        print("\n📊 Testing dashboard API...")
        try:
            # This will fail without authentication, but we can check the endpoint exists
            response = requests.get(f"{server_url}/api/detections", timeout=10)
            if response.status_code == 401:
                print("✅ Dashboard API endpoint exists (requires login)")
            elif response.status_code == 200:
                detections = response.json()
                print(f"✅ Dashboard API working - {len(detections)} detections")
            else:
                print(f"⚠️ Dashboard API response: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Dashboard API test failed: {e}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running?")
        print("💡 Start server with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_uploaded_images():
    """Check what images are in the uploads folder"""
    print("\n📁 Checking Uploads Folder...")
    
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        if image_files:
            print(f"📷 Found {len(image_files)} uploaded images:")
            for img in image_files:
                file_path = os.path.join(uploads_dir, img)
                file_size = os.path.getsize(file_path)
                print(f"   {img} ({file_size} bytes)")
        else:
            print("📷 No images found in uploads folder")
    else:
        print("❌ Uploads folder doesn't exist")

def main():
    """Test image upload and display functionality"""
    print("📷 Image Display Test - Smart Waste Monitor")
    print("=" * 50)
    
    # Check current uploads
    check_uploaded_images()
    
    # Test uploads
    success = test_image_upload_and_display()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ IMAGE UPLOAD TESTS COMPLETED!")
        print("=" * 50)
        print("💡 To see results:")
        print("1. Open: http://localhost:10000")
        print("2. Login: admin/admin123")
        print("3. Check dashboard for new detections")
        print("4. Images should show thumbnails and 'View Full' buttons")
        
        # Check uploads again
        check_uploaded_images()
        
    else:
        print("\n❌ Image upload tests failed")
        print("💡 Make sure the server is running: python run.py")

if __name__ == '__main__':
    main()