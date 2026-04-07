#!/usr/bin/env python3
"""
Complete Working System Setup
MongoDB Atlas + Email Alerts + Image Attachments
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import gridfs

# Load environment variables
load_dotenv()

def test_mongodb_atlas():
    """Test MongoDB Atlas connection with your active cluster"""
    print("🗄️ Testing MongoDB Atlas Connection...")
    
    # Your cluster details from screenshot
    MONGODB_URI = "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/waste_monitoring?retryWrites=true&w=majority"
    
    try:
        print("🔗 Connecting to Cluster0 (AWS Mumbai)...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
        
        # Test connection with ping
        client.admin.command('ping')
        print("✅ MongoDB Atlas connected successfully!")
        
        # Access database
        db = client.waste_monitoring
        print(f"📊 Database: {db.name}")
        
        # Test collections
        detections = db.detections
        
        # Insert test detection
        test_detection = {
            'timestamp': datetime.now().isoformat(),
            'detection_status': 'WASTE DETECTED',
            'confidence': 89.5,
            'location': 'ESP32 Camera Point',
            'detected_objects': ['bottle', 'cup'],
            'detection_details': 'Plastic waste detected on roadside',
            'test': True
        }
        
        result = detections.insert_one(test_detection)
        print(f"✅ Test detection stored: {result.inserted_id}")
        
        # Retrieve test detection
        stored_doc = detections.find_one({'_id': result.inserted_id})
        if stored_doc:
            print("✅ Test detection retrieved successfully")
            print(f"   Status: {stored_doc['detection_status']}")
            print(f"   Confidence: {stored_doc['confidence']}%")
        
        # Test GridFS for image storage
        fs = gridfs.GridFS(db)
        
        # Test image storage (if sample image exists)
        test_images = [
            "static/images/garbage on roadside.jpg",
            "static/images/750x450_garbage-in-public-places.jpg"
        ]
        
        for img_path in test_images:
            if os.path.exists(img_path):
                print(f"📷 Testing image storage: {img_path}")
                with open(img_path, 'rb') as f:
                    file_id = fs.put(f, filename=os.path.basename(img_path))
                print(f"✅ Image stored in GridFS: {file_id}")
                
                # Test image retrieval
                stored_image = fs.get(file_id)
                if stored_image:
                    print("✅ Image retrieved from GridFS successfully")
                
                # Clean up test image
                fs.delete(file_id)
                print("🧹 Test image cleaned up")
                break
        
        # Clean up test detection
        detections.delete_one({'_id': result.inserted_id})
        print("🧹 Test detection cleaned up")
        
        # Show cluster stats
        stats = db.command("dbstats")
        print(f"📊 Database size: {stats.get('dataSize', 0)} bytes")
        print(f"📁 Collections: {db.list_collection_names()}")
        
        client.close()
        return True, client, db
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {e}")
        return False, None, None

def setup_gmail_app_password():
    """Interactive Gmail app password setup"""
    print("\n📧 Gmail App Password Setup...")
    
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    
    print(f"📨 Email: {EMAIL_USER}")
    print(f"🔑 Current password length: {len(EMAIL_PASS)} characters")
    
    if len(EMAIL_PASS) != 16:
        print("\n⚠️ Gmail app password should be exactly 16 characters")
        print("📋 Steps to generate app password:")
        print("   1. Go to https://myaccount.google.com/security")
        print("   2. Enable 2-Step Verification (if not enabled)")
        print("   3. Go to 2-Step Verification → App passwords")
        print("   4. Select 'Mail' and 'Other (Custom name)'")
        print("   5. Enter 'Smart Waste Monitor'")
        print("   6. Copy the 16-character password")
        
        print(f"\n💡 From your screenshot, the app password is: iovm minl nmwx lint")
        print("💡 Remove spaces: iovmminlnmwxlint")
        
        new_password = input("\n🔑 Enter your 16-character app password (or press Enter to use current): ").strip()
        
        if new_password and len(new_password) == 16:
            # Update .env file
            with open('.env', 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('EMAIL_PASS='):
                    lines[i] = f'EMAIL_PASS={new_password}'
                    break
            
            with open('.env', 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Password updated in .env file")
            EMAIL_PASS = new_password
        elif not new_password:
            # Try removing spaces from current password
            EMAIL_PASS = EMAIL_PASS.replace(' ', '')
            if len(EMAIL_PASS) == 16:
                # Update .env file
                with open('.env', 'r') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('EMAIL_PASS='):
                        lines[i] = f'EMAIL_PASS={EMAIL_PASS}'
                        break
                
                with open('.env', 'w') as f:
                    f.write('\n'.join(lines))
                
                print("✅ Removed spaces from password and updated .env")
    
    return EMAIL_PASS

def test_email_with_detection_image():
    """Test email alert with waste detection image"""
    print("\n📧 Testing Email Alert with Detection Image...")
    
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = setup_gmail_app_password()
    EMAIL_TO = os.environ.get('EMAIL_TO', '')
    
    # Find detection image
    test_images = [
        "static/images/garbage on roadside.jpg",
        "static/images/750x450_garbage-in-public-places.jpg",
        "static/images/roadsie waste collection.avif"
    ]
    
    detection_image = None
    for img in test_images:
        if os.path.exists(img):
            detection_image = img
            break
    
    if not detection_image:
        print("❌ No detection image found for testing")
        return False
    
    print(f"📷 Using detection image: {detection_image}")
    
    try:
        # Create waste detection alert email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🚨 WASTE DETECTED - Smart Monitoring Alert"
        
        # Realistic waste detection email body
        body = f"""
🚨 WASTE DETECTION ALERT 🚨

📅 Detection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Confidence Level: 92.3%
📍 Location: ESP32 Camera Point - Roadside Monitoring
🤖 AI System: YOLO Object Detection v8

📊 DETECTION DETAILS:
• Objects Detected: Plastic bottles (94.2%), Food containers (89.7%), Paper waste (76.3%)
• Risk Level: HIGH - Multiple waste items detected
• Area Status: Requires immediate attention

⚡ IMMEDIATE ACTION REQUIRED:
1. 🚛 Dispatch waste collection team to location
2. 📋 Update collection status in dashboard  
3. 📊 Monitor area for recurring waste accumulation
4. 🔄 Schedule regular monitoring for this location

📷 DETECTION IMAGE:
High-resolution image of detected waste is attached to this email.
Image captured by ESP32 camera with AI analysis overlay.

🌐 SYSTEM DASHBOARD:
Access your monitoring dashboard for detailed analytics:
• Real-time detection status
• Historical waste patterns  
• Collection team coordination
• Area-wise waste statistics

📱 MOBILE ACCESS:
Dashboard is mobile-responsive for field team access.

🔧 TECHNICAL DETAILS:
• Camera ID: ESP32_CAM_001
• Detection Algorithm: YOLOv8 Neural Network
• Processing Time: 0.8 seconds
• Image Resolution: 1024x768
• Storage: MongoDB Atlas Cloud Database

Smart Waste Monitoring System
🤖 AI-Powered Detection | 📷 ESP32 Cameras | ☁️ Cloud Storage | 📧 Instant Alerts
AI for Cleaner Cities 🌱

---
This is an automated alert from your Smart Waste Monitoring System.
For technical support or system configuration, access the admin dashboard.

System Status: ✅ OPERATIONAL | Database: ✅ CONNECTED | Email: ✅ ACTIVE
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach detection image
        print("📎 Attaching detection image...")
        with open(detection_image, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            
            # Create descriptive filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"waste_detected_{timestamp}.jpg"
            
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
        
        print("📡 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Authenticating with Gmail...")
        server.login(EMAIL_USER, EMAIL_PASS)
        
        print("📤 Sending waste detection alert...")
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
        
        print("✅ Waste detection email sent successfully!")
        print(f"📬 Check your inbox: {EMAIL_TO}")
        print("📷 Detection image should be attached")
        print("🚨 Email simulates real waste detection alert")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("💡 Check app password - should be 16 characters without spaces")
        return False
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def create_sample_detection_data():
    """Create sample detection data in MongoDB"""
    print("\n📊 Creating Sample Detection Data...")
    
    try:
        MONGODB_URI = "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/waste_monitoring?retryWrites=true&w=majority"
        client = MongoClient(MONGODB_URI)
        db = client.waste_monitoring
        detections = db.detections
        
        # Sample detection records
        sample_detections = [
            {
                'timestamp': '2026-03-03T10:30:00',
                'detection_status': 'WASTE DETECTED',
                'confidence': 94.2,
                'location': 'ESP32 Camera Point A',
                'detected_objects': ['bottle', 'cup', 'food_container'],
                'detection_details': 'Multiple plastic waste items detected'
            },
            {
                'timestamp': '2026-03-03T11:15:00',
                'detection_status': 'NO WASTE',
                'confidence': 0.0,
                'location': 'ESP32 Camera Point A',
                'detected_objects': [],
                'detection_details': 'Area clean - no waste detected'
            },
            {
                'timestamp': '2026-03-03T12:45:00',
                'detection_status': 'WASTE DETECTED',
                'confidence': 87.6,
                'location': 'ESP32 Camera Point B',
                'detected_objects': ['bottle', 'paper'],
                'detection_details': 'Plastic bottle and paper waste detected'
            }
        ]
        
        # Insert sample data
        result = detections.insert_many(sample_detections)
        print(f"✅ Created {len(result.inserted_ids)} sample detection records")
        
        # Show current data count
        total_count = detections.count_documents({})
        print(f"📊 Total detections in database: {total_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def main():
    """Setup complete working system"""
    print("🚀 Smart Waste Monitor - Complete System Setup")
    print("=" * 60)
    print("Setting up MongoDB Atlas + Email Alerts + Image Attachments")
    print("=" * 60)
    
    # Test MongoDB Atlas
    mongo_success, client, db = test_mongodb_atlas()
    
    # Test Email with Image
    email_success = test_email_with_detection_image()
    
    # Create sample data if MongoDB works
    if mongo_success:
        sample_data_success = create_sample_detection_data()
    else:
        sample_data_success = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 SYSTEM SETUP SUMMARY")
    print("=" * 60)
    
    print(f"🗄️ MongoDB Atlas: {'✅ CONNECTED' if mongo_success else '❌ FAILED'}")
    print(f"📧 Email Alerts: {'✅ WORKING' if email_success else '❌ FAILED'}")
    print(f"📊 Sample Data: {'✅ CREATED' if sample_data_success else '❌ FAILED'}")
    
    if mongo_success and email_success:
        print("\n🎉 SYSTEM FULLY OPERATIONAL!")
        print("✅ MongoDB Atlas cluster connected")
        print("✅ Email alerts working with image attachments")
        print("✅ Ready for ESP32 integration")
        print("✅ Ready for production deployment")
        
        print(f"\n📧 Email alerts configured for: {os.environ.get('EMAIL_TO')}")
        print("🗄️ Data stored in MongoDB Atlas (AWS Mumbai)")
        print("🚀 System ready to detect and alert waste!")
        
        print("\n🎯 Next Steps:")
        print("1. Run the Flask app: python run.py")
        print("2. Test web interface: http://localhost:10000")
        print("3. Connect ESP32 cameras")
        print("4. Deploy to production (Render)")
        
    else:
        print("\n⚠️ System needs attention:")
        if not mongo_success:
            print("   🗄️ Fix MongoDB Atlas connection")
        if not email_success:
            print("   📧 Fix Gmail app password")
        
        print("\n💡 Run this script again after fixing issues")

if __name__ == '__main__':
    main()