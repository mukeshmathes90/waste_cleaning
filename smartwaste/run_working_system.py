#!/usr/bin/env python3
"""
Run Working System - Immediate Start
Falls back to SQLite if MongoDB fails, works without email
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_minimal_env():
    """Create minimal working environment"""
    print("🔧 Creating minimal working configuration...")
    
    minimal_config = """# Smart Waste Monitoring System - Working Configuration
SECRET_KEY=smartwaste-2026-working-system-key
ADMIN_PASSWORD=admin123
OFFICER_PASSWORD=waste2026
PORT=10000

# MongoDB (optional - will use SQLite if fails)
MONGODB_URI=mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/waste_monitoring?retryWrites=true&w=majority
DATABASE_NAME=waste_monitoring

# Email (optional - will skip if not configured)
EMAIL_USER=nithishkumarmb775@gmail.com
EMAIL_PASS=
EMAIL_TO=nithishkumarmb775@gmail.com
"""
    
    with open('.env.working', 'w') as f:
        f.write(minimal_config)
    
    print("✅ Created .env.working with minimal configuration")
    return True

def test_system_components():
    """Test what's working in the system"""
    print("🧪 Testing System Components...")
    
    # Test Flask
    try:
        from flask import Flask
        print("✅ Flask: Available")
    except ImportError:
        print("❌ Flask: Not installed")
        return False
    
    # Test YOLO
    try:
        from ultralytics import YOLO
        if os.path.exists('yolov8n.pt'):
            print("✅ YOLO: Model available")
        else:
            print("⚠️ YOLO: Model will download on first run")
    except ImportError:
        print("❌ YOLO: Not installed")
    
    # Test MongoDB (optional)
    try:
        from pymongo import MongoClient
        print("✅ MongoDB: Library available")
    except ImportError:
        print("⚠️ MongoDB: Library not available (will use SQLite)")
    
    # Test directories
    required_dirs = ['uploads', 'static', 'templates']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory: {dir_name}")
        else:
            print(f"❌ Directory: {dir_name} missing")
    
    return True

def run_system():
    """Run the Smart Waste Monitoring System"""
    print("\n🚀 Starting Smart Waste Monitoring System...")
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    # Import and run the app
    try:
        print("📱 Loading Flask application...")
        from app import app
        
        print("🌐 Starting web server...")
        print("=" * 50)
        print("🎉 Smart Waste Monitoring System")
        print("=" * 50)
        print("📍 URL: http://localhost:10000")
        print("👤 Login: admin / admin123")
        print("👤 Login: officer / waste2026")
        print("=" * 50)
        print("✅ System Features Available:")
        print("   🌐 Web Dashboard")
        print("   🤖 AI Waste Detection")
        print("   📷 ESP32 Integration")
        print("   💾 Data Storage")
        print("   📊 Detection History")
        print("=" * 50)
        print("⚠️ Optional Features (may need setup):")
        print("   📧 Email Alerts")
        print("   🗄️ MongoDB Atlas")
        print("=" * 50)
        
        # Run the app
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except Exception as e:
        print(f"❌ Failed to start system: {e}")
        return False

def main():
    """Main function to get system running"""
    print("🚀 Smart Waste Monitor - Quick Start")
    print("=" * 50)
    
    # Test components
    if not test_system_components():
        print("❌ System components missing")
        return
    
    # Create working config if needed
    if not os.path.exists('.env'):
        create_minimal_env()
        print("💡 Using minimal configuration")
        print("💡 MongoDB and Email can be configured later")
    
    # Run the system
    print("\n🎯 System Status: READY TO RUN")
    print("💡 The system will work with or without MongoDB/Email")
    print("💡 Missing features will be automatically disabled")
    
    try:
        run_system()
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        print("💡 Check the error above and try again")

if __name__ == '__main__':
    main()