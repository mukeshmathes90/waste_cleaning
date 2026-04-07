# 🔧 MongoDB + Email Setup Guide

## 🚨 Current Issues & Solutions

### 1. MongoDB Atlas Connection Issue
**Error**: `The DNS query name does not exist: _mongodb._tcp.cluster0.mongodb.net`

**Possible Causes:**
- Network/DNS issues
- Incorrect cluster name
- Firewall blocking MongoDB Atlas
- Cluster not fully provisioned

**Solutions:**

#### Option A: Fix MongoDB Connection
1. **Verify Cluster Status**:
   - Go to [MongoDB Atlas Dashboard](https://cloud.mongodb.com/)
   - Check if cluster is running (green status)
   - Wait if cluster is still provisioning

2. **Get Correct Connection String**:
   - In Atlas dashboard, click "Connect"
   - Choose "Connect your application"
   - Copy the exact connection string
   - Replace `<password>` with: `SH5opjXilokse2pJ`

3. **Update .env file**:
   ```bash
   MONGODB_URI=your-exact-connection-string-from-atlas
   ```

#### Option B: Use SQLite (Temporary)
If MongoDB issues persist, the system can fall back to SQLite:
```python
# The app will automatically use SQLite if MongoDB fails
# No configuration needed - just run the app
```

### 2. Gmail Authentication Issue
**Error**: `Username and Password not accepted`

**Solutions:**

#### Step 1: Verify 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Ensure "2-Step Verification" is ON
3. If not enabled, enable it first

#### Step 2: Generate New App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "2-Step Verification"
3. Scroll to "App passwords"
4. Click "App passwords"
5. Select "Mail" and "Other (Custom name)"
6. Enter "Smart Waste Monitor"
7. Click "Generate"
8. **Copy the 16-character password exactly**

#### Step 3: Update Configuration
```bash
# Edit smartwaste/.env
EMAIL_PASS=your-new-16-character-password
```

## 🧪 Test Configuration

### Test MongoDB Only
```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.environ.get('MONGODB_URI'))
client.admin.command('ping')
print('MongoDB OK')
"
```

### Test Email Only
```bash
python -c "
import smtplib, os
from dotenv import load_dotenv
load_dotenv()
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
print('Email OK')
server.quit()
"
```

### Test Complete System
```bash
python test_email_with_mongodb.py
```

## 🚀 Run System Without Full Setup

The Smart Waste Monitoring System can run even if MongoDB or email isn't working:

```bash
# Run the app (will use SQLite if MongoDB fails)
python run.py

# Access at: http://localhost:10000
# Login: admin / admin123
```

**Features that work without MongoDB/Email:**
- ✅ Web interface and dashboard
- ✅ AI waste detection
- ✅ Image upload and analysis
- ✅ ESP32 integration
- ✅ Local SQLite storage
- ⚠️ Email alerts (disabled if not configured)
- ⚠️ MongoDB storage (falls back to SQLite)

## 📧 Email Alert Preview

When working, you'll receive emails like this:

```
Subject: 🚨 Waste Detected - Smart Monitoring Alert

🚨 WASTE DETECTION ALERT 🚨

📅 Detection Time: 2026-03-03 14:30:45
🎯 Confidence Level: 87.5%
📍 Location: ESP32 Camera Point
🤖 AI System: YOLO Object Detection

📊 DETECTION DETAILS:
Detected objects: bottle (89.2%), cup (76.8%)

⚡ IMMEDIATE ACTION REQUIRED:
1. Dispatch waste collection team
2. Update collection status in dashboard
3. Monitor for recurring issues

📷 ATTACHED IMAGE:
High-resolution detection image attached

Smart Waste Monitoring System
AI for Cleaner Cities 🌱
```

## 🔄 Priority Setup Order

### 1. Get System Running (Immediate)
```bash
cd smartwaste
python run.py
# Test web interface first
```

### 2. Fix Email (High Priority)
- Generate new Gmail app password
- Test email alerts
- Verify image attachments work

### 3. Fix MongoDB (Optional)
- Verify Atlas cluster status
- Update connection string
- Test database storage

## 📞 Troubleshooting

### MongoDB Issues
- Check Atlas dashboard for cluster status
- Try different connection string formats
- Check network/firewall settings
- Contact MongoDB Atlas support if needed

### Email Issues
- Ensure 2FA is enabled on Gmail
- Generate fresh app password
- Check for typos in email configuration
- Test with simple email first

### System Issues
- Check all environment variables
- Verify file permissions
- Check Python package versions
- Review error logs

---

**Remember**: The system works great even without MongoDB/email. Fix these as bonus features! 🚀