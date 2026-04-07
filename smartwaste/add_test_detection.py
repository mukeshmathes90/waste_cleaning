#!/usr/bin/env python3
"""
Add Test Detection with Image
Create a test detection record with an actual image file
"""

import sqlite3
import os
import shutil
from datetime import datetime

def copy_sample_image_to_uploads():
    """Copy a sample image to uploads folder for testing"""
    print("📷 Copying sample image to uploads folder...")
    
    # Find sample image
    sample_images = [
        "static/images/garbage on roadside.jpg",
        "static/images/750x450_garbage-in-public-places.jpg"
    ]
    
    sample_image = None
    for img in sample_images:
        if os.path.exists(img):
            sample_image = img
            break
    
    if not sample_image:
        print("❌ No sample image found")
        return None
    
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Copy image to uploads with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_test_waste.jpg"
    dest_path = os.path.join('uploads', filename)
    
    shutil.copy2(sample_image, dest_path)
    print(f"✅ Copied {sample_image} to {dest_path}")
    
    return dest_path

def add_test_detection_with_image():
    """Add a test detection record with actual image"""
    print("📊 Adding test detection with image...")
    
    # Copy sample image
    image_path = copy_sample_image_to_uploads()
    if not image_path:
        return False
    
    try:
        conn = sqlite3.connect('waste_monitoring.db')
        c = conn.cursor()
        
        # Add test detection
        test_detection = (
            datetime.now().isoformat(),
            image_path,
            'WASTE DETECTED',
            92.7,
            'ESP32 Camera Test Point',
            'bottle, plastic_bag, food_container',
            'Test detection: Multiple waste items detected for dashboard testing'
        )
        
        c.execute('''INSERT INTO detections 
                    (timestamp, image_path, detection_status, confidence, location, detected_objects, detection_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', test_detection)
        
        conn.commit()
        
        # Get the inserted record
        c.execute('SELECT * FROM detections WHERE image_path = ?', (image_path,))
        result = c.fetchone()
        
        if result:
            print("✅ Test detection added successfully!")
            print(f"   ID: {result[0]}")
            print(f"   Status: {result[3]}")
            print(f"   Confidence: {result[4]}%")
            print(f"   Objects: {result[6]}")
            print(f"   Image: {result[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to add test detection: {e}")
        return False

def verify_image_accessibility():
    """Verify that uploaded images can be accessed"""
    print("\n🔍 Verifying image accessibility...")
    
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"📷 Found {len(image_files)} images in uploads:")
        for img in image_files:
            file_path = os.path.join(uploads_dir, img)
            file_size = os.path.getsize(file_path)
            print(f"   ✅ {img} ({file_size:,} bytes)")
            
        return len(image_files) > 0
    else:
        print("❌ Uploads directory not found")
        return False

def show_dashboard_instructions():
    """Show instructions for viewing the dashboard"""
    print("\n" + "=" * 50)
    print("📊 DASHBOARD VIEWING INSTRUCTIONS")
    print("=" * 50)
    print("1. Start the Flask app:")
    print("   python run.py")
    print()
    print("2. Open your browser:")
    print("   http://localhost:10000")
    print()
    print("3. Login to dashboard:")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("4. Check the dashboard:")
    print("   ✅ You should see waste detection records")
    print("   ✅ Each record should show a thumbnail image")
    print("   ✅ Click 'View Full' to see full-size image")
    print("   ✅ Images should load properly")
    print()
    print("5. Test image upload:")
    print("   ✅ Use the 'Test Image Upload' section")
    print("   ✅ Upload a waste image")
    print("   ✅ Check if it appears in the dashboard")

def main():
    """Add test detection and show instructions"""
    print("📷 Dashboard Image Display Setup")
    print("=" * 50)
    
    # Add test detection with image
    success = add_test_detection_with_image()
    
    if success:
        # Verify images
        images_ok = verify_image_accessibility()
        
        if images_ok:
            print("\n✅ TEST DETECTION WITH IMAGE ADDED!")
            print("✅ Images are accessible in uploads folder")
            print("✅ Dashboard should now display images properly")
            
            # Show instructions
            show_dashboard_instructions()
            
        else:
            print("⚠️ Detection added but image verification failed")
    else:
        print("❌ Failed to add test detection")

if __name__ == '__main__':
    main()