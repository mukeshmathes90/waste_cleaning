# 📧 Gmail Setup Guide for Smart Waste Monitoring

## 🔧 Gmail App Password Setup

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click "Security" in the left sidebar
3. Under "Signing in to Google", click "2-Step Verification"
4. Follow the setup process if not already enabled

### Step 2: Generate App Password
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click "Security" → "2-Step Verification"
3. Scroll down to "App passwords"
4. Click "App passwords"
5. Select "Mail" and "Other (Custom name)"
6. Enter "Smart Waste Monitor" as the name
7. Click "Generate"
8. **Copy the 16-character password** (no spaces)

### Step 3: Configure Environment Variables
Update your `.env` file:
```bash
EMAIL_USER=nithishkumarmb775@gmail.com
EMAIL_PASS=your-16-character-app-password-here
EMAIL_TO=nithishkumarmb775@gmail.com
```

## 🧪 Test Email Configuration

### Run Email Test
```bash
python test_email.py
```

### Expected Output (Success)
```
✅ Email sent successfully!
📬 Check your inbox: nithishkumarmb775@gmail.com
```

## 🚨 Troubleshooting

### Issue: Authentication Failed
**Possible Causes:**
1. App password has spaces (remove them)
2. 2FA not enabled on Gmail account
3. App password not generated correctly
4. Using regular password instead of app password

**Solutions:**
1. Remove all spaces from app password
2. Enable 2-factor authentication first
3. Generate new app password
4. Use app password, not regular Gmail password

### Issue: SMTP Connection Failed
**Possible Causes:**
1. Firewall blocking SMTP
2. Network connectivity issues
3. Gmail SMTP settings incorrect

**Solutions:**
1. Check firewall settings
2. Test internet connection
3. Verify SMTP settings: `smtp.gmail.com:587`

### Issue: Email Not Received
**Possible Causes:**
1. Email in spam folder
2. Gmail filters blocking
3. Incorrect recipient email

**Solutions:**
1. Check spam/junk folder
2. Check Gmail filters
3. Verify email address spelling

## 📋 Gmail Security Checklist

### Before Testing
- [ ] 2-Factor Authentication enabled
- [ ] App password generated (16 characters)
- [ ] App password copied without spaces
- [ ] Email address correct: `nithishkumarmb775@gmail.com`

### After Testing
- [ ] Test email received successfully
- [ ] Waste alert email received
- [ ] No authentication errors
- [ ] Emails not in spam folder

## 🔒 Security Notes

### App Password Security
- App passwords bypass 2FA for specific apps
- Keep app password secure (don't share)
- Revoke app password if compromised
- Use different app passwords for different services

### Email Content
- Waste alerts contain detection details
- Images may be attached to alerts
- Timestamps and locations included
- No sensitive personal data transmitted

## 🚀 Production Deployment

### Render Environment Variables
Set these in your Render dashboard:
```
EMAIL_USER=nithishkumarmb775@gmail.com
EMAIL_PASS=your-app-password-here
EMAIL_TO=nithishkumarmb775@gmail.com
```

### Testing in Production
1. Deploy to Render with email config
2. Test with ESP32 or manual upload
3. Verify alerts are received
4. Monitor email delivery logs

---

**Need Help?** 
1. Check Gmail account security settings
2. Verify 2FA is enabled
3. Generate fresh app password
4. Test with simple email first

**Smart Waste Monitoring System** | Email Alerts Ready 📧🌱