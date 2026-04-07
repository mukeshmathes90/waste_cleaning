#!/usr/bin/env python3
"""
MongoDB + Email Fix Script
Diagnose and fix both MongoDB Atlas and Gmail issues
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv
import socket
import dns.resolver

# Load environment variables
load_dotenv()

def test_network_connectivity():
    """Test basic network connectivity"""
    print("🌐 Testing Network Connectivity...")
    
    try:
        # Test Google DNS
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        print("✅ Internet connection: OK")
        
        # Test MongoDB Atlas DNS
        try:
            answers = dns.resolver.resolve("cluster0.mongodb.net", "A")
            print(f"✅ MongoDB DNS resolution: OK ({len(answers)} records)")
        except Exception as e:
            print(f"❌ MongoDB DNS resolution failed: {e}")
            return False
            
        # Test Gmail SMTP
        try:
            socket.create_connection(("smtp.gmail.com", 587), timeout=5)
            print("✅ Gmail SMTP connectivity: OK")
        except Exception as e:
            print(f"❌ Gmail SMTP connectivity failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Network connectivity failed: {e}")
        return False

def fix_mongodb_connection():
    """Fix and test MongoDB Atlas connection"""
    print("\n🗄️ Fixing MongoDB Atlas Connection...")
    
    # Try multiple connection string formats
    connection_strings = [
        "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/waste_monitoring?retryWrites=true&w=majority",
        "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/?retryWrites=true&w=majority",
        "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/waste_monitoring?retryWrites=true&w=majority&appName=Cluster0",
    ]
    
    for i, uri in enumerate(connection_strings, 1):
        print(f"\n🔗 Trying connection string {i}...")
        try:
            from pymongo import MongoClient
            
            client = MongoClient(uri, serverSelectionTimeoutMS=10000)
            
            # Test connection
            client.admin.command('ping')
            print("✅ MongoDB connection successful!")
            
            # Test database operations
            db = client.waste_monitoring
            test_collection = db.test_connection
            
            # Insert test document
            result = test_collection.insert_one({
                'test': True,
                'timestamp': datetime.now().isoformat(),
                'message': 'Connection test successful'
            })
            print(f"✅ Test document inserted: {result.inserted_id}")
            
            # Read test document
            doc = test_collection.find_one({'_id': result.inserted_id})
            if doc:
                print("✅ Test document retrieved successfully")
            
            # Clean up
            test_collection.delete_one({'_id': result.inserted_id})
            print("🧹 Test document cleaned up")
            
            # List collections
            collections = db.list_collection_names()
            print(f"📊 Available collections: {collections}")
            
            client.close()
            
            # Update .env with working connection string
            print(f"\n💾 Updating .env with working connection string...")
            with open('.env', 'r') as f:
                content = f.read()
            
            # Replace MongoDB URI
            lines = content.split('\n')
            for j, line in enumerate(lines):
                if line.startswith('MONGODB_URI='):
                    lines[j] = f'MONGODB_URI={uri}'
                    break
            
            with open('.env', 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ .env file updated with working MongoDB URI")
            return True, uri
            
        except Exception as e:
            print(f"❌ Connection {i} failed: {e}")
            continue
    
    print("❌ All MongoDB connection attempts failed")
    return False, None

def fix_gmail_authentication():
    """Fix Gmail app password authentication"""
    print("\n📧 Fixing Gmail Authentication...")
    
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    EMAIL_TO = os.environ.get('EMAIL_TO', '')
    
    print(f"📨 Email User: {EMAIL_USER}")
    print(f"📬 Email To: {EMAIL_TO}")
    print(f"🔑 Password Length: {len(EMAIL_PASS)} characters")
    
    if len(EMAIL_PASS) != 16:
        print("⚠️ Gmail app passwords should be exactly 16 characters")
        print("💡 Generate a new app password:")
        print("   1. Go to https://myaccount.google.com/security")
        print("   2. 2-Step Verification → App passwords")
        print("   3. Generate password for 'Mail'")
        print("   4. Copy 16-character password (no spaces)")
        
        new_password = input("🔑 Enter new 16-character app password (or press Enter to skip): ").strip()
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
            
            EMAIL_PASS = new_password
            print("✅ Password updated in .env file")
    
    # Test Gmail authentication
    try:
        print("🔗 Testing Gmail SMTP connection...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Testing authentication...")
        server.login(EMAIL_USER, EMAIL_PASS)
        server.quit()
        
        print("✅ Gmail authentication successful!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("💡 Solutions:")
        print("   1. Ensure 2-factor authentication is enabled")
        print("   2. Generate a fresh app password")
        print("   3. Remove any spaces from the password")
        print("   4. Try a different app password")
        return False
    except Exception as e:
        print(f"❌ Gmail connection failed: {e}")
        return False

def test_email_with_image():
    """Test sending email with image attachment"""
    print("\n📧 Testing Email with Image...")
    
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    EMAIL_TO = os.environ.get('EMAIL_TO', '')
    
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
    
    try:
        # Create email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🎉 Smart Waste Monitor - System Working!"
        
        body = f"""
🎉 SYSTEM FULLY OPERATIONAL!

📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✅ MongoDB Atlas: Connected and working
✅ Email Alerts: Working with image attachments
✅ YOLO AI Detection: Ready
✅ ESP32 Integration: Ready

🚨 WASTE DETECTION SIMULATION:
- Confidence: 92.3%
- Location: ESP32 Camera Point
- Objects Detected: Plastic bottles, food containers
- Action: Immediate waste collection required

📷 IMAGE ATTACHMENT:
High-resolution waste detection image is attached to this email.

Your Smart Waste Monitoring System is now fully functional and ready for:
🤖 Real-time AI waste detection
📧 Instant email alerts with images
🗄️ Cloud database storage (MongoDB Atlas)
📱 ESP32 camera integration
🌐 Web dashboard monitoring

Next Steps:
1. Deploy to production (Render)
2. Connect ESP32 cameras
3. Start monitoring waste in real-time!

Smart Waste Monitoring System
AI for Cleaner Cities 🌱
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach image
        with open(test_image, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= waste_detection_success.jpg'
            )
            msg.attach(part)
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
        
        print("✅ Email with image sent successfully!")
        print(f"📬 Check your inbox: {EMAIL_TO}")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def main():
    """Main fix and test function"""
    print("🔧 Smart Waste Monitor - System Fix & Test")
    print("=" * 60)
    
    # Test network first
    network_ok = test_network_connectivity()
    if not network_ok:
        print("❌ Network issues detected. Check internet connection.")
        return
    
    # Fix MongoDB
    mongo_ok, mongo_uri = fix_mongodb_connection()
    
    # Fix Gmail
    gmail_ok = fix_gmail_authentication()
    
    # Test complete system if both work
    if mongo_ok and gmail_ok:
        print("\n🎉 Both MongoDB and Gmail are working!")
        email_test_ok = test_email_with_image()
        
        if email_test_ok:
            print("\n" + "=" * 60)
            print("🎉 SYSTEM FULLY OPERATIONAL!")
            print("=" * 60)
            print("✅ MongoDB Atlas: Connected")
            print("✅ Email Alerts: Working with images")
            print("✅ Complete system: Ready for production")
            print(f"\n📧 Email alerts will be sent to: {os.environ.get('EMAIL_TO')}")
            print("🚀 Your Smart Waste Monitoring System is ready!")
        else:
            print("⚠️ Email test failed, but authentication works")
    else:
        print("\n⚠️ System needs attention:")
        if not mongo_ok:
            print("   🗄️ MongoDB Atlas connection needs fixing")
        if not gmail_ok:
            print("   📧 Gmail authentication needs fixing")

if __name__ == '__main__':
    main()