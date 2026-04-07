# 🚀 Render Deployment Guide

## 📋 Prerequisites
- GitHub account with your code pushed
- Render account (free tier available)
- ESP32 device configured

## 🌐 Step 1: Deploy to Render

### Option A: Using render.yaml (Recommended)
1. Push your code to GitHub
2. Go to Render Dashboard
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml`
6. Click "Create Web Service"

### Option B: Manual Setup
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure manually:
   - **Name**: smart-waste-monitoring
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: Free

## 🔧 Step 2: Configure Environment Variables

After deployment, go to your service → **Settings** → **Environment** and add:

### Required Variables
```
SECRET_KEY=your-random-secret-key-here
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
EMAIL_TO=recipient@gmail.com
ADMIN_PASSWORD=your-secure-admin-password
OFFICER_PASSWORD=your-officer-password
```

### Optional Variables
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname
DATABASE_NAME=waste_monitoring
ESP_CAM_STREAM_URL=http://your-esp32-ip:81/stream
ESP_CAM_LOCATION=ESP32 Camera Point
LIVE_YOLO_FPS=2
LIVE_YOLO_MIN_CONF=0.3
LIVE_YOLO_EMAIL_COOLDOWN_SEC=60
```

## 📡 Step 3: Get Your Render URL

After deployment, your app will be available at:
`https://your-app-name.onrender.com`

## 🔌 Step 4: Configure ESP32

1. Open `esp32_render_template.ino`
2. Update these lines:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";           // Your WiFi name
   const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password
   String renderServerUrl = "https://your-app-name.onrender.com";  // Your Render URL
   ```

3. Upload to ESP32

## ✅ Step 5: Test the System

### Test Render App
1. Visit: `https://your-app-name.onrender.com`
2. Login with admin/officer credentials
3. Check health: `https://your-app-name.onrender.com/health`
4. Check config: `https://your-app-name.onrender.com/config`

### Test ESP32 Connection
1. ESP32 Serial Monitor should show:
   ```
   ✅ WiFi connected!
   📡 ESP IP Address: 192.168.x.x
   📤 Upload to: https://your-app-name.onrender.com/analyze
   ✅ Upload successful! Code: 200
   ```

2. Visit ESP32 stream: `http://esp32-ip:81/stream`

### Test Full System
1. Place waste objects in front of ESP32 camera
2. Check dashboard for live YOLO detection
3. Check email for waste alerts
4. Verify snapshots are saved

## 🐛 Troubleshooting

### Common Issues

**Render App Not Starting**
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` is correct

**ESP32 Cannot Connect**
- Verify WiFi credentials
- Check Render URL is correct (use https://)
- Ensure Render app is running

**No Email Alerts**
- Verify Gmail App Password (not regular password)
- Check EMAIL_USER and EMAIL_TO are correct
- Test with `/test-email` endpoint

**Camera Stream Not Working**
- Check camera wiring
- Verify camera model in code
- Try different frame sizes

### Health Check Endpoints
- `/health` - System status
- `/config` - Configuration info
- `/test-email` - Test email (requires login)

## 📱 Monitoring

### Render Dashboard
- Monitor service health
- Check response times
- View error logs

### ESP32 Serial Monitor
- WiFi connection status
- Upload success/failure
- Camera capture status

### Email Alerts
- Should receive emails when waste is detected
- Check spam folder if not receiving

## 🔄 Auto-Deployment

With `render.yaml`, your app will automatically redeploy when you push to GitHub:
1. Make changes to code
2. `git add . && git commit -m "Update"`
3. `git push origin main`
4. Render will automatically build and deploy

## 💡 Pro Tips

1. **Use MongoDB Atlas** for better scalability
2. **Monitor Render free tier limits** (750 hours/month)
3. **Set up custom domain** for production
4. **Implement retry logic** in ESP32 for reliability
5. **Add error logging** for debugging

## 🎯 Next Steps

1. Deploy to Render
2. Test with ESP32
3. Monitor for 24 hours
4. Add more cameras if needed
5. Scale to production if required
