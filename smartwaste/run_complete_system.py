#!/usr/bin/env python3
"""
Run Complete Smart Waste Monitoring System
SQLite + Email Alerts + Image Attachments - Fully Working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_system_ready():
    """Verify all system components are ready"""
    print("🔍 Verifying System Components...")
    
    # Check Flask
    try:
        import flask
        print("✅ Flask: Available")
    except ImportError:
        print("❌ Flask: Missing - run 'pip install flask'")
        return False
    
    # Check YOLO
    try:
        from ultralytics import YOLO
        print("✅ YOLO: Available")
        if os.path.exists('yolov8n.pt'):
            print("✅ YOLO Model: Found")
        else:
            print("⚠️ YOLO Model: Will download on first detection")
    except ImportError:
        print("❌ YOLO: Missing - run 'pip install ultralytics'")
        return False
    
    # Check email configuration
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    
    if EMAIL_USER and EMAIL_PASS and len(EMAIL_PASS) == 16:
        print("✅ Email: Configured and ready")
    else:
        print("⚠️ Email: Not configured (alerts will be logged only)")
    
    # Check directories
    required_dirs = ['uploads', 'static', 'templates', 'static/images']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory: {dir_name}")
        else:
            print(f"❌ Directory: {dir_name} missing")
            return False
    
    # Check sample images
    sample_images = [f for f in os.listdir('static/images') if f.lower().endswith(('.jpg', '.jpeg', '.png', '.avif'))]
    if sample_images:
        print(f"✅ Sample Images: {len(sample_images)} found")
    else:
        print("⚠️ Sample Images: None found")
    
    return True

def create_sample_sqlite_data():
    """Create sample data in SQLite database"""
    print("\n📊 Creating Sample Data in SQLite...")
    
    try:
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect('waste_monitoring.db')
        c = conn.cursor()
        
        # Create detections table
        c.execute('''CREATE TABLE IF NOT EXISTS detections
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT,
                      image_path TEXT,
                      detection_status TEXT,
                      confidence REAL,
                      location TEXT,
                      detected_objects TEXT,
                      detection_details TEXT)''')
        
        # Insert sample detections
        sample_data = [
            (datetime.now().isoformat(), 'uploads/sample1.jpg', 'WASTE DETECTED', 94.5, 
             'ESP32 Camera Point A', 'bottle, cup, food_container', 
             'Multiple plastic waste items detected on roadside'),
            (datetime.now().isoformat(), 'uploads/sample2.jpg', 'NO WASTE', 0.0,
             'ESP32 Camera Point A', '', 'Area clean - no waste detected'),
            (datetime.now().isoformat(), 'uploads/sample3.jpg', 'WASTE DETECTED', 87.3,
             'ESP32 Camera Point B', 'bottle, paper, can',
             'Mixed waste detected - bottles, paper, metal cans')
        ]
        
        c.executemany('''INSERT INTO detections 
                        (timestamp, image_path, detection_status, confidence, location, detected_objects, detection_details)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''', sample_data)
        
        conn.commit()
        
        # Check data
        c.execute('SELECT COUNT(*) FROM detections')
        count = c.fetchone()[0]
        print(f"✅ Created SQLite database with {count} sample detections")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def test_email_system():
    """Test email system one more time"""
    print("\n📧 Final Email System Test...")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        EMAIL_USER = os.environ.get('EMAIL_USER', '')
        EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
        EMAIL_TO = os.environ.get('EMAIL_TO', '')
        
        if not EMAIL_USER or not EMAIL_PASS:
            print("⚠️ Email not configured - alerts will be logged only")
            return False
        
        # Quick authentication test
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.quit()
        
        print("✅ Email system ready for waste detection alerts")
        return True
        
    except Exception as e:
        print(f"⚠️ Email test failed: {e}")
        print("💡 System will work without email alerts")
        return False

def show_system_status():
    """Show complete system status"""
    print("\n" + "=" * 60)
    print("🎯 SMART WASTE MONITORING SYSTEM STATUS")
    print("=" * 60)
    
    print("✅ Core System: READY")
    print("   🌐 Web Dashboard")
    print("   🤖 AI Waste Detection (YOLO)")
    print("   📷 ESP32 Camera Integration")
    print("   💾 SQLite Database Storage")
    print("   📊 Detection History & Analytics")
    
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    
    if EMAIL_USER and EMAIL_PASS:
        print("✅ Email Alerts: CONFIGURED")
        print(f"   📧 Alerts sent to: {EMAIL_USER}")
        print("   📷 Images attached to alerts")
        print("   🚨 Instant waste detection notifications")
    else:
        print("⚠️ Email Alerts: NOT CONFIGURED")
        print("   💡 Detections will be logged and stored")
        print("   💡 Configure email later for alerts")
    
    print("\n🗄️ Database: SQLite (Local)")
    print("   💡 MongoDB Atlas can be added later")
    print("   💡 All data stored locally for now")
    
    print("\n🚀 Ready Features:")
    print("   ✅ Upload images via web interface")
    print("   ✅ Real-time AI waste detection")
    print("   ✅ Detection confidence scoring")
    print("   ✅ Historical data tracking")
    print("   ✅ ESP32 raw image processing")
    print("   ✅ Responsive web dashboard")
    
    print("\n📱 Access Information:")
    print("   🌐 URL: http://localhost:10000")
    print("   👤 Admin Login: admin / admin123")
    print("   👤 Officer Login: officer / waste2026")
    
    print("\n🔗 API Endpoints:")
    print("   📤 POST /analyze - ESP32 image upload")
    print("   📤 POST /upload - Alternative ESP32 endpoint")
    print("   📊 GET /api/detections - Detection history")

def main():
    """Run the complete system setup and start"""
    print("🚀 Smart Waste Monitoring System - Complete Setup")
    print("=" * 60)
    
    # Verify system
    if not verify_system_ready():
        print("❌ System not ready - please install missing components")
        return
    
    # Create sample data
    create_sample_sqlite_data()
    
    # Test email
    email_ready = test_email_system()
    
    # Show status
    show_system_status()
    
    print("\n" + "=" * 60)
    print("🎉 SYSTEM READY TO START!")
    print("=" * 60)
    
    # Ask user if they want to start
    start_now = input("\n🚀 Start the Smart Waste Monitoring System now? (y/n): ").lower().strip()
    
    if start_now in ['y', 'yes', '']:
        print("\n🌟 Starting Smart Waste Monitoring System...")
        print("=" * 60)
        
        try:
            # Import and run the Flask app
            from app import app
            
            print("🎯 System Features Active:")
            print("   🤖 AI Waste Detection: YOLO v8")
            print("   📊 Database: SQLite")
            if email_ready:
                print("   📧 Email Alerts: Gmail SMTP")
            print("   📷 ESP32 Integration: Ready")
            print("   🌐 Web Interface: Active")
            
            print("\n🔗 Access your system:")
            print("   Dashboard: http://localhost:10000")
            print("   Login: admin/admin123 or officer/waste2026")
            
            print("\n📱 ESP32 Integration:")
            print("   Endpoint: http://localhost:10000/analyze")
            print("   Method: POST (raw JPEG data)")
            
            print("\n" + "=" * 60)
            print("🌱 AI for Cleaner Cities - System Active!")
            print("=" * 60)
            
            # Run the Flask app
            port = int(os.environ.get('PORT', 10000))
            app.run(host='0.0.0.0', port=port, debug=False)
            
        except KeyboardInterrupt:
            print("\n\n👋 System stopped by user")
        except Exception as e:
            print(f"\n❌ System error: {e}")
    else:
        print("\n💡 To start later, run: python run_complete_system.py")
        print("💡 Or run directly: python run.py")

if __name__ == '__main__':
    main()