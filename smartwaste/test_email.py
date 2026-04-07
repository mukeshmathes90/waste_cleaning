#!/usr/bin/env python3
"""
Email Configuration Test Script
Test Gmail SMTP with app password
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_configuration():
    """Test email sending with Gmail app password"""
    print("📧 Testing Email Configuration...")
    
    # Get email credentials from environment
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    EMAIL_TO = os.environ.get('EMAIL_TO', '')
    
    print(f"📨 From: {EMAIL_USER}")
    print(f"📬 To: {EMAIL_TO}")
    print(f"🔑 Password: {'*' * len(EMAIL_PASS) if EMAIL_PASS else 'NOT SET'}")
    
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ Email credentials not configured!")
        print("💡 Please check your .env file")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🧪 Smart Waste Monitor - Email Test"
        
        body = f"""
        📧 EMAIL CONFIGURATION TEST
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        System: Smart Waste Monitoring System
        Status: Email alerts are working! ✅
        
        This is a test email to verify that waste detection alerts 
        will be sent successfully when waste is detected by the AI system.
        
        🤖 AI Detection Ready
        📷 ESP32 Camera Ready  
        📧 Email Alerts Ready
        ♻️ Smart Waste Monitoring Active
        
        Best regards,
        Smart Waste Monitoring System
        AI for Cleaner Cities 🌱
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP
        print("🔗 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Authenticating...")
        server.login(EMAIL_USER, EMAIL_PASS)
        
        print("📤 Sending test email...")
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_TO, text)
        server.quit()
        
        print("✅ Email sent successfully!")
        print(f"📬 Check your inbox: {EMAIL_TO}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("💡 Check your Gmail app password")
        print("💡 Make sure 2-factor authentication is enabled")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_waste_detection_email():
    """Test waste detection alert email"""
    print("\n🚨 Testing Waste Detection Alert Email...")
    
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    EMAIL_TO = os.environ.get('EMAIL_TO', '')
    
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ Email not configured")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🚨 Waste Detected - Smart Monitoring Alert"
        
        body = f"""
        WASTE DETECTION ALERT 🚨
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Confidence: 87.5%
        Location: ESP32 Camera Point - Roadside Monitoring
        Detection: Plastic bottles and food waste detected
        
        Please take immediate action for waste collection.
        
        📍 Location Details:
        - Camera ID: ESP32_CAM_001
        - GPS Coordinates: Available in dashboard
        - Image: Attached (simulated)
        
        🎯 Action Required:
        1. Dispatch waste collection team
        2. Update collection status in dashboard
        3. Monitor for recurring issues
        
        Smart Waste Monitoring System
        AI for Cleaner Cities 🌱
        
        Dashboard: https://your-app.onrender.com/dashboard
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_TO, text)
        server.quit()
        
        print("✅ Waste detection alert sent!")
        return True
        
    except Exception as e:
        print(f"❌ Alert email failed: {e}")
        return False

def main():
    """Run email tests"""
    print("🚀 Smart Waste Monitor - Email Test Suite")
    print("=" * 50)
    
    # Test basic email
    basic_test = test_email_configuration()
    
    if basic_test:
        # Test waste detection alert
        alert_test = test_waste_detection_email()
    else:
        alert_test = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 EMAIL TEST SUMMARY")
    print("=" * 50)
    
    if basic_test:
        print("✅ Basic Email Test: PASS")
    else:
        print("❌ Basic Email Test: FAIL")
    
    if alert_test:
        print("✅ Waste Alert Email: PASS")
    else:
        print("❌ Waste Alert Email: FAIL")
    
    if basic_test and alert_test:
        print("\n🎉 All email tests passed!")
        print("📧 Waste detection alerts will be sent to: nithishkumarmb775@gmail.com")
        print("💡 Your Smart Waste Monitoring System is ready!")
    else:
        print("\n⚠️ Email configuration needs attention")
        print("💡 Check Gmail app password and 2FA settings")

if __name__ == '__main__':
    main()