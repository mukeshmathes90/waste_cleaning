# 🚀 Deployment Guide - Smart Waste Monitoring System

## Local Development

### Quick Start (Windows)
```bash
# Double-click start.bat or run:
start.bat
```

### Manual Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

Visit: **http://localhost:10000**

## 🌐 Render Deployment (Production)

### Step 1: Prepare Repository
1. Push this `smartwaste/` folder to GitHub
2. Ensure all files are committed

### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository containing `smartwaste/`

### Step 3: Configure Service
```yaml
Name: smart-waste-monitor
Environment: Python 3
Region: Choose closest to your location
Branch: main
Root Directory: smartwaste
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### Step 4: Environment Variables (Optional)
```
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
PORT=10000
```

### Step 5: Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Your app will be live at: `https://your-app-name.onrender.com`

## 📱 ESP32 Integration

### Arduino Code Example
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* serverURL = "https://your-app.onrender.com/analyze";

void sendImage() {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) return;
    
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "multipart/form-data");
    
    // Send image data
    int httpResponseCode = http.POST(fb->buf, fb->len);
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.println("Detection result: " + response);
    }
    
    esp_camera_fb_return(fb);
    http.end();
}
```

## 🔧 Configuration

### Login Credentials
- **Admin**: `admin` / `admin123`
- **Officer**: `officer` / `waste2026`

### File Structure
```
smartwaste/
├── app.py              # Main Flask app
├── requirements.txt    # Dependencies
├── Procfile           # Render config
├── yolov8n.pt         # YOLO model (auto-downloaded)
├── run.py             # Local startup script
├── start.bat          # Windows batch file
├── uploads/           # Image storage
├── templates/         # HTML pages
├── static/           # CSS, JS, Images
└── waste_monitoring.db # SQLite database (auto-created)
```

## 🧪 Testing

### Test Image Upload
```bash
curl -X POST -F "image=@test_image.jpg" http://localhost:10000/analyze
```

### Test API
```bash
# Get detections (requires login)
curl -b cookies.txt http://localhost:10000/api/detections
```

## 🔍 Troubleshooting

### Common Issues

**1. YOLO Model Missing**
- Model downloads automatically on first run
- If failed, manually download: `wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt`

**2. Port Already in Use**
- Change port in `run.py`: `app.run(port=8000)`
- Or kill existing process: `taskkill /f /im python.exe`

**3. Dependencies Error**
- Update pip: `python -m pip install --upgrade pip`
- Install manually: `pip install flask ultralytics opencv-python-headless`

**4. Database Issues**
- Delete `waste_monitoring.db` to reset
- App will recreate database automatically

### Performance Tips
- Use `gunicorn` for production (included in requirements)
- Enable gzip compression on Render
- Use CDN for static files in production
- Monitor memory usage with large images

## 📊 Monitoring

### Logs
- Local: Check terminal output
- Render: View logs in dashboard
- Database: SQLite browser for `waste_monitoring.db`

### Metrics
- Detection accuracy
- Response times
- Storage usage
- Email delivery status

## 🔒 Security

### Production Checklist
- [ ] Change default passwords
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up proper email credentials
- [ ] Configure CORS if needed
- [ ] Monitor API usage
- [ ] Regular database backups

## 📞 Support

For issues or questions:
1. Check logs for error messages
2. Verify all dependencies installed
3. Test with sample images
4. Contact development team

---
**Smart Waste Monitoring System** | AI for Cleaner Cities 🌱