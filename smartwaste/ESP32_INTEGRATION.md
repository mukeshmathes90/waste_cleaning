# 📷 ESP32 Integration Guide

## ✅ ESP32 Compatibility Checklist

### ✅ CHECK 1 — Raw JPEG Support
**Status**: ✅ **FIXED** - Route now handles both:
- ESP32 raw JPEG data via `request.data`
- Web form multipart data via `request.files`

```python
# ESP32 raw JPEG handling
if request.data:
    with open(filepath, "wb") as f:
        f.write(request.data)
```

### ✅ CHECK 2 — Route Names
**Status**: ✅ **BOTH SUPPORTED**
- `/analyze` - Main endpoint
- `/upload` - ESP32 compatible alias

Both routes work with ESP32!

### ✅ CHECK 3 — Content-Type Handling
**Status**: ✅ **CORRECT** - Uses `request.data` for ESP32

### ✅ CHECK 4 — Upload Folder
**Status**: ✅ **EXISTS** - Auto-created on startup
```python
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

### ✅ CHECK 5 — Model Loading
**Status**: ✅ **GLOBAL** - Loaded once at startup
```python
model = YOLO("yolov8n.pt")  # Global variable
```

## 🔧 ESP32 Arduino Code

### Complete Working Example
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server configuration
const char* serverURL = "https://your-app.onrender.com/analyze";
// Alternative: const char* serverURL = "https://your-app.onrender.com/upload";

void setup() {
    Serial.begin(115200);
    
    // Initialize camera
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
    
    // Initialize camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    // Capture image every 30 seconds
    sendImageToServer();
    delay(30000);
}

void sendImageToServer() {
    // Capture image
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        return;
    }
    
    Serial.printf("Image captured: %d bytes\n", fb->len);
    
    // Send to server
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/octet-stream");
    
    // Send raw JPEG data
    int httpResponseCode = http.POST(fb->buf, fb->len);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.printf("HTTP Response: %d\n", httpResponseCode);
        Serial.println("Response: " + response);
        
        // Parse JSON response (optional)
        if (response.indexOf("\"waste_detected\":true") > 0) {
            Serial.println("🚨 WASTE DETECTED!");
        } else {
            Serial.println("✅ No waste detected");
        }
    } else {
        Serial.printf("HTTP Error: %d\n", httpResponseCode);
    }
    
    // Clean up
    esp_camera_fb_return(fb);
    http.end();
}
```

## 🧪 Testing ESP32 Integration

### Test with curl (Simulates ESP32)
```bash
# Test raw JPEG upload
curl -X POST \
  -H "Content-Type: application/octet-stream" \
  --data-binary @test_image.jpg \
  http://localhost:10000/analyze

# Expected response:
{
  "success": true,
  "waste_detected": false,
  "confidence": 0.0,
  "timestamp": "2026-03-03T12:00:00",
  "image_path": "uploads/20260303_120000_esp32.jpg"
}
```

### Test with Python (Simulates ESP32)
```python
import requests

# Read image file
with open('test_image.jpg', 'rb') as f:
    image_data = f.read()

# Send to server
response = requests.post(
    'http://localhost:10000/analyze',
    data=image_data,
    headers={'Content-Type': 'application/octet-stream'}
)

print(response.json())
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "waste_detected": true,
  "confidence": 85.6,
  "timestamp": "2026-03-03T12:00:00.123456",
  "image_path": "uploads/20260303_120000_esp32.jpg"
}
```

### Error Response
```json
{
  "error": "No image data provided"
}
```

## 🔧 Troubleshooting

### Common Issues

**1. ESP32 Connection Failed**
- Check WiFi credentials
- Verify server URL is correct
- Test with curl first

**2. Image Upload Failed**
- Ensure camera is initialized properly
- Check image buffer size
- Verify Content-Type header

**3. Server Returns Error**
- Check server logs
- Verify route is `/analyze` or `/upload`
- Test with sample image first

**4. No Detection Results**
- Verify YOLO model is loaded
- Check image quality and lighting
- Test with known waste objects

### Debug Commands
```bash
# Check server logs
python run.py  # Watch console output

# Test server endpoint
curl -X POST http://localhost:10000/analyze

# Check uploaded images
ls uploads/
```

## 🚀 Production Deployment

### Render Configuration
1. Deploy Flask app to Render
2. Update ESP32 code with Render URL:
   ```cpp
   const char* serverURL = "https://your-app-name.onrender.com/analyze";
   ```
3. Test connection from ESP32

### Security Considerations
- Use HTTPS in production (automatic on Render)
- Consider API key authentication for production
- Monitor upload frequency to prevent abuse

---

**Status**: ✅ **ESP32 READY** - Both `/analyze` and `/upload` endpoints support raw JPEG data

**Smart Waste Monitoring System** | ESP32 Compatible 📷🤖