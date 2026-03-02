# Smart Waste Monitoring System ♻️

AI-powered waste detection system using ESP32 cameras, YOLO object detection, and cloud monitoring.

## Features

- 🤖 **AI Waste Detection**: YOLO-based object detection
- 📷 **ESP32 Integration**: IoT camera monitoring
- ☁️ **Cloud Dashboard**: Real-time web interface
- 📧 **Email Alerts**: Automatic notifications
- 🏢 **Municipal Portal**: Officer login system
- 📊 **Data Tracking**: Detection history and analytics

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (IMPORTANT!)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
# SECURITY: Change default passwords before deployment!
```

### 3. Download YOLO Model
Download `yolov8n.pt` from [Ultralytics](https://github.com/ultralytics/ultralytics) and place it in the project root:
```bash
# The app will automatically download it on first run, or manually:
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### 4. Run Locally
```bash
python run.py
```
Visit: http://localhost:10000

### 5. Deploy to Render
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app`
4. **IMPORTANT**: Configure environment variables in Render dashboard
5. Deploy!

## Login Credentials

**Default credentials (CHANGE THESE!):**
- Admin: `admin` / `admin123` (set via ADMIN_PASSWORD env var)
- Officer: `officer` / `waste2026` (set via OFFICER_PASSWORD env var)

**⚠️ SECURITY WARNING**: Change default passwords before deployment!

## API Endpoints

### POST /analyze
Upload image for waste detection:
```bash
curl -X POST -F "image=@waste_image.jpg" http://localhost:10000/analyze
```

### GET /api/detections
Get recent detections (requires login):
```bash
curl http://localhost:10000/api/detections
```

## ESP32 Integration

Send images to the `/analyze` endpoint:
```cpp
// ESP32 code example
HTTPClient http;
http.begin("http://your-app.onrender.com/analyze");
http.addHeader("Content-Type", "multipart/form-data");
// Add image data and POST
```

## Project Structure

```
smartwaste/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Render deployment config
├── yolov8n.pt         # YOLO model (download separately)
├── uploads/           # Uploaded images storage
├── templates/         # HTML templates
│   ├── home.html      # Landing page
│   ├── login.html     # Officer login
│   └── dashboard.html # Admin dashboard
└── static/           # Static assets
    ├── css/style.css # Styles
    ├── js/main.js    # JavaScript
    └── images/       # Sample images
```

## Development Team

- **Yamuna S** - Project Lead
- **Ashwanth S** - AI Developer  
- **Nithishkumar M B** - Backend Developer
- **Mukhil Krishnaa D** - IoT Specialist
- **Mohammed Zuhair B** - Frontend Developer
- **Kishore S** - System Architect

## Environment Variables

**Required for production deployment:**

```bash
# Security (REQUIRED)
SECRET_KEY=your-long-random-secret-key-here
ADMIN_PASSWORD=your-secure-admin-password
OFFICER_PASSWORD=your-secure-officer-password

# Email alerts (optional)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_TO=municipal@city.gov

# Optional
PORT=10000
```

**Setting up in Render:**
1. Go to your service dashboard
2. Click "Environment" tab
3. Add each variable above
4. Redeploy service

## License

MIT License - Smart Waste Monitoring System 2026