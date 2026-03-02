#!/usr/bin/env python3
"""
Smart Waste Monitoring System - Test Script
Verify all components are working correctly
"""

import os
import sys
import sqlite3
from datetime import datetime

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    try:
        import flask
        print("✅ Flask imported successfully")
        
        import cv2
        print("✅ OpenCV imported successfully")
        
        import numpy as np
        print("✅ NumPy imported successfully")
        
        from ultralytics import YOLO
        print("✅ Ultralytics YOLO imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_yolo_model():
    """Test if YOLO model exists and loads"""
    print("\n🤖 Testing YOLO model...")
    try:
        if os.path.exists("yolov8n.pt"):
            print("✅ YOLO model file found")
            from ultralytics import YOLO
            model = YOLO("yolov8n.pt")
            print("✅ YOLO model loaded successfully")
            return True
        else:
            print("❌ YOLO model file not found")
            return False
    except Exception as e:
        print(f"❌ YOLO model error: {e}")
        return False

def test_directories():
    """Test if all required directories exist"""
    print("\n📁 Testing directories...")
    required_dirs = ['uploads', 'static', 'templates', 'static/css', 'static/js', 'static/images']
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            all_exist = False
    
    return all_exist

def test_templates():
    """Test if all template files exist"""
    print("\n📄 Testing templates...")
    required_templates = ['templates/home.html', 'templates/login.html', 'templates/dashboard.html']
    
    all_exist = True
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            all_exist = False
    
    return all_exist

def test_static_files():
    """Test if static files exist"""
    print("\n🎨 Testing static files...")
    required_files = ['static/css/style.css', 'static/js/main.js']
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database...")
    try:
        from app import init_db
        init_db()
        
        # Test database connection
        conn = sqlite3.connect('waste_monitoring.db')
        c = conn.cursor()
        c.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = c.fetchall()
        conn.close()
        
        if tables:
            print("✅ Database created and accessible")
            print(f"✅ Tables found: {[table[0] for table in tables]}")
            return True
        else:
            print("❌ No tables found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be created"""
    print("\n🌐 Testing Flask app...")
    try:
        from app import app
        print("✅ Flask app created successfully")
        
        # Test routes exist
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ['/', '/login', '/dashboard', '/analyze', '/logout']
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} exists")
            else:
                print(f"❌ Route {route} missing")
        
        return True
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def test_sample_images():
    """Test if sample images exist"""
    print("\n🖼️ Testing sample images...")
    image_dir = 'static/images'
    
    if os.path.exists(image_dir):
        images = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.avif'))]
        if images:
            print(f"✅ Found {len(images)} sample images:")
            for img in images:
                print(f"   📷 {img}")
            return True
        else:
            print("❌ No sample images found")
            return False
    else:
        print("❌ Images directory not found")
        return False

def main():
    """Run all tests"""
    print("🚀 Smart Waste Monitoring System - System Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("YOLO Model", test_yolo_model),
        ("Directories", test_directories),
        ("Templates", test_templates),
        ("Static Files", test_static_files),
        ("Database", test_database),
        ("Flask App", test_flask_app),
        ("Sample Images", test_sample_images)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to run.")
        print("💡 Run 'python run.py' to start the application")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please fix issues before running.")
        print("💡 Check the error messages above for details")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)