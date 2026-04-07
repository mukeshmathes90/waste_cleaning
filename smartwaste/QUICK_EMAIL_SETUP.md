# ⚡ Quick Email Setup - Smart Waste Monitor

## 🎯 Current Configuration
- **Email**: nithishkumarmb775@gmail.com
- **App Password**: Generated (needs verification)
- **Recipient**: nithishkumarmb775@gmail.com

## 🔧 Quick Fix Steps

### 1. Verify Gmail App Password
The app password from your screenshot: `iovm minl nmwx lint`

**Remove spaces and try:**
```
iovmminlnmwxlint
```

### 2. Alternative: Generate New App Password
1. Go to [Google Account](https://myaccount.google.com/)
2. Security → 2-Step Verification → App passwords
3. Generate new password for "Mail"
4. Copy the 16-character code (no spaces)

### 3. Update Configuration
Edit `smartwaste/.env`:
```bash
EMAIL_USER=nithishkumarmb775@gmail.com
EMAIL_PASS=your-new-app-password-here
EMAIL_TO=nithishkumarmb775@gmail.com
```

### 4. Test Email
```bash
cd smartwaste
python test_email.py
```

## 🚀 Quick Test Without Email (For Now)

If email setup is taking time, you can still test the system:

### 1. Run the Application
```bash
cd smartwaste
python run.py
```

### 2. Access Dashboard
- Open: http://localhost:10000
- Login: admin / admin123
- Test image upload in dashboard

### 3. Check Detection Logs
The system will log detection results even without email:
```
Email alert skipped - credentials not configured. Detection: 85.6%
```

## 📧 Email Alert Preview

When working, you'll receive emails like:
```
Subject: 🚨 Waste Detected - Smart Monitoring Alert

WASTE DETECTION ALERT 🚨

Time: 2026-03-03 12:30:45
Confidence: 87.5%
Location: ESP32 Camera Point

Please take immediate action for waste collection.

Smart Waste Monitoring System
AI for Cleaner Cities 🌱
```

## 🔄 Enable Email Later

You can enable email alerts anytime by:
1. Setting up Gmail app password correctly
2. Updating `.env` file
3. Restarting the application

The system works perfectly without email - alerts are just a bonus feature!

---

**Priority**: Get the system running first, fix email second 🚀