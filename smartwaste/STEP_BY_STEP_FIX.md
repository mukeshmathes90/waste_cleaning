# 🔧 Step-by-Step Fix Guide

## 🎯 Current Issues to Fix

### 1. MongoDB Atlas DNS Issue ❌
**Error**: `The DNS query name does not exist: _mongodb._tcp.cluster0.mongodb.net`

### 2. Gmail Authentication Issue ❌  
**Error**: `Username and Password not accepted`

---

## 🗄️ Fix MongoDB Atlas Connection

### Step 1: Get Correct Connection String
1. **Go to MongoDB Atlas Dashboard**: https://cloud.mongodb.com/
2. **Click your Cluster0** (the one showing in your screenshot)
3. **Click "Connect" button**
4. **Choose "Connect your application"**
5. **Copy the connection string** - it should look like:
   ```
   mongodb+srv://nithishkumarmb775_db_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 2: Update Connection String
The connection string from Atlas will have a different format. Replace `<password>` with: `SH5opjXilokse2pJ`

### Step 3: Network Access Settings
1. **In Atlas Dashboard**, go to "Network Access"
2. **Click "Add IP Address"**
3. **Choose "Allow Access from Anywhere"** (0.0.0.0/0)
4. **Click "Confirm"**

---

## 📧 Fix Gmail App Password

### Step 1: Generate Fresh App Password
1. **Go to**: https://myaccount.google.com/security
2. **Click "2-Step Verification"** (enable if not already)
3. **Scroll down to "App passwords"**
4. **Click "App passwords"**
5. **Select "Mail"** and **"Other (Custom name)"**
6. **Enter**: "Smart Waste Monitor"
7. **Click "Generate"**
8. **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)

### Step 2: Update .env File
```bash
# Remove ALL spaces from the app password
EMAIL_PASS=abcdefghijklmnop
```

---

## 🧪 Quick Test Commands

### Test MongoDB Connection
```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
uri = os.environ.get('MONGODB_URI')
print(f'Testing: {uri[:50]}...')
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
client.admin.command('ping')
print('✅ MongoDB Connected!')
"
```

### Test Gmail Authentication
```bash
python -c "
import smtplib, os
from dotenv import load_dotenv
load_dotenv()
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
print('✅ Gmail Connected!')
server.quit()
"
```

---

## 🔄 Alternative: Run Without MongoDB/Email

If you want to test the system while fixing these issues:

### Create Temporary .env
```bash
# Copy current .env to backup
cp .env .env.backup

# Create minimal working .env
cat > .env << EOF
SECRET_KEY=smartwaste-2026-temp-key
ADMIN_PASSWORD=admin123
OFFICER_PASSWORD=waste2026
PORT=10000
EOF
```

### Run System
```bash
python run.py
# Access: http://localhost:10000
# Login: admin / admin123
```

**This will work with:**
- ✅ Web interface
- ✅ AI detection  
- ✅ Local SQLite database
- ✅ ESP32 integration
- ❌ Email alerts (disabled)
- ❌ MongoDB storage (uses SQLite)

---

## 📋 Checklist

### MongoDB Atlas
- [ ] Cluster is running (green status in Atlas)
- [ ] Network Access allows your IP (0.0.0.0/0)
- [ ] Connection string is correct format
- [ ] Password matches exactly: `SH5opjXilokse2pJ`

### Gmail App Password  
- [ ] 2-Factor Authentication enabled
- [ ] Fresh app password generated
- [ ] Password is exactly 16 characters
- [ ] No spaces in password
- [ ] Updated in .env file

### System Test
- [ ] MongoDB connection test passes
- [ ] Gmail authentication test passes  
- [ ] Full system test passes
- [ ] Email with image received

---

## 🆘 If Still Having Issues

### MongoDB Alternatives
1. **Use different cluster region**
2. **Create new cluster** 
3. **Use SQLite temporarily** (system works fine)

### Gmail Alternatives
1. **Try different Google account**
2. **Use different email service** (Outlook, Yahoo)
3. **Disable email alerts temporarily**

### Get Help
1. **Check Atlas status page**: https://status.cloud.mongodb.com/
2. **Check Gmail help**: https://support.google.com/mail/answer/185833
3. **Test with minimal configuration first**

---

**Remember**: The Smart Waste Monitoring System works perfectly even without MongoDB/email. These are enhancement features that can be added later! 🚀