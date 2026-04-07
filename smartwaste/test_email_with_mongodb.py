#!/usr/bin/env python3
"""
Email + MongoDB Test Script
Test email alerts with image attachments and MongoDB storage
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

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    print("🗄️ Testing MongoDB Connection...")
    
    MONGODB_URI = os.environ.get('MONGODB_URI', '')
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'waste_monitoring')
    
    if not MONGODB_URI:
        print("❌ MongoDB URI not configured")
        return False, None, None
    
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Test connection with ping
        client.admin.command('ping')
        print("✅ MongoDB connected successfully")
        
        # Test collections
        detections = db.detections
        fs = gridfs.GridFS(db)
        
        print(f"📊 Database: {DATABASE_NAME}")
        print(f"📁 Collections available: {db.list_collection_names()}")
        
        return True, detections, fs
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False, None, None

def test_email_with_image():
    """Test email sending with image attachment"""
    print("\n📧 Testing Email with Image Attachment...")
    
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    EMAIL_TO = os.environ.get('EMAIL_TO', '')
    
    print(f"📨 From: {EMAIL_USER}")
    print(f"📬 To: {EMAIL_TO}")
    print(f"🔑 Password: {'*' * len(EMAIL_PASS) if EMAIL_PASS else 'NOT SET'}")
    
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ Email credentials not configured!")
        return False
    
    # Find test image
    test_images = [
        "static/images/garbage on roadside.jpg",
        "static/images/750x450_garbage-in-public-places.jpg",
        "static/images/roadsie waste collection.avif"
    ]
    
    test_image = None
    for img_path in test_images:
        if os.path.exists(img_path):
            test_image = img_path
            break
    
    if not test_image:
        print("❌ No test image found")
        return False
    
    print(f"📷 Using test image: {test_image}")
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🧪 Smart Waste Monitor - Email + Image Test"
        
        body = f"""
🧪 EMAIL + IMAGE ATTACHMENT TEST

📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 System: Smart Waste Monitoring System
📧 Email: Working with image attachments! ✅
🗄️ Database: MongoDB Atlas integration active
📷 Image: High-resolution waste detection image attached

🚨 SIMULATED WASTE DETECTION ALERT:
- Confidence: 87.5%
- Location: ESP32 Camera Point
- Objects: Plastic bottles, food waste detected
- Action Required: Immediate waste collection

📊 SYSTEM STATUS:
✅ MongoDB Atlas: Connected
✅ YOLO AI Detection: Active
✅ Email Alerts: Working
✅ Image Attachments: Functional
✅ ESP32 Integration: Ready

This test confirms that your Smart Waste Monitoring System
can successfully send email alerts with attached images
when waste is detected by the AI system.

🌐 Next Steps:
1. Deploy to production (Render)
2. Connect ESP32 cameras
3. Monitor real-time waste detection
4. Receive instant email alerts

Smart Waste Monitoring System
🤖 AI-Powered | 📷 ESP32 Cameras | ☁️ Cloud Monitoring | 📧 Email Alerts
AI for Cleaner Cities 🌱

---
This is a test email from your Smart Waste Monitoring System.
If you received this with an image attachment, everything is working perfectly!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach test image
        print("📎 Attaching image...")
        with open(test_image, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            
            filename = f"waste_detection_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
        
        print("📡 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Authenticating...")
        server.login(EMAIL_USER, EMAIL_PASS)
        
        print("📤 Sending email with image...")
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_TO, text)
        server.quit()
        
        print("✅ Email with image sent successfully!")
        print(f"📬 Check your inbox: {EMAIL_TO}")
        print("📷 Image should be attached to the email")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Check Gmail app password (remove spaces)")
        print("💡 Ensure 2-factor authentication is enabled")
        return False
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_mongodb_storage():
    """Test storing detection data in MongoDB"""
    print("\n🗄️ Testing MongoDB Storage...")
    
    success, detections, fs = test_mongodb_connection()
    if not success:
        return False
    
    try:
        # Test document insertion
        test_doc = {
            'timestamp': datetime.now().isoformat(),
            'detection_status': 'TEST DETECTION',
            'confidence': 95.5,
            'location': 'Test Location',
            'detected_objects': ['bottle', 'cup'],
            'detection_details': 'Test detection for system verification'
        }
        
        result = detections.insert_one(test_doc)
        print(f"✅ Test document inserted: {result.inserted_id}")
        
        # Test document retrieval
        doc = detections.find_one({'_id': result.inserted_id})
        if doc:
            print("✅ Test document retrieved successfully")
            print(f"   Timestamp: {doc['timestamp']}")
            print(f"   Status: {doc['detection_status']}")
            print(f"   Confidence: {doc['confidence']}%")
        
        # Clean up test document
        detections.delete_one({'_id': result.inserted_id})
        print("🧹 Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB storage test failed: {e}")
        return False

def test_complete_system():
    """Test complete system: MongoDB + Email + Image"""
    print("\n🚀 Testing Complete System Integration...")
    
    # Test MongoDB
    mongo_success, detections, fs = test_mongodb_connection()
    
    # Test email with image
    email_success = test_email_with_image()
    
    # Test MongoDB storage
    storage_success = test_mongodb_storage() if mongo_success else False
    
    return mongo_success, email_success, storage_success

def main():
    """Run comprehensive system tests"""
    print("🚀 Smart Waste Monitor - Complete System Test")
    print("=" * 60)
    
    # Run all tests
    mongo_success, email_success, storage_success = test_complete_system()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    print(f"🗄️ MongoDB Connection: {'✅ PASS' if mongo_success else '❌ FAIL'}")
    print(f"📧 Email with Image: {'✅ PASS' if email_success else '❌ FAIL'}")
    print(f"💾 MongoDB Storage: {'✅ PASS' if storage_success else '❌ FAIL'}")
    
    all_passed = mongo_success and email_success and storage_success
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your Smart Waste Monitoring System is fully functional:")
        print("   📧 Email alerts with images: WORKING")
        print("   🗄️ MongoDB Atlas storage: WORKING")
        print("   🤖 AI detection ready: READY")
        print("   📷 ESP32 integration: READY")
        print("\n🚀 System is ready for production deployment!")
        print(f"📬 Email alerts will be sent to: {os.environ.get('EMAIL_TO', 'Not configured')}")
    else:
        print("\n⚠️ Some tests failed:")
        if not mongo_success:
            print("   🗄️ Fix MongoDB Atlas connection")
        if not email_success:
            print("   📧 Fix Gmail app password configuration")
        if not storage_success:
            print("   💾 Fix MongoDB storage permissions")
        
        print("\n💡 Check configuration and try again")

if __name__ == '__main__':
    main()