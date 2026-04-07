#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <WiFiClient.h>

// ============ CONFIGURATION ============
// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Render Server Configuration
String renderServerUrl = "https://your-app-name.onrender.com";  // UPDATE AFTER DEPLOYMENT
String analyzeEndpoint = "/analyze";
String streamEndpoint = "/stream";

// Camera Configuration
#define CAMERA_MODEL_AI_THINKER
// Camera pins for AI Thinker model
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM     -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM      26
#define SIOC_GPIO_NUM      27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Timing Configuration
unsigned long lastUploadTime = 0;
const unsigned long uploadInterval = 10000;  // 10 seconds between uploads
const int maxRetries = 3;
const int retryDelay = 2000;  // 2 seconds

// ===================================

WebServer server(81);  // Stream on port 81

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Smart Waste ESP32 - Render Version ===");

  // Initialize WiFi
  setupWiFi();
  
  // Initialize Camera
  setupCamera();
  
  // Start Web Server
  setupWebServer();
  
  Serial.println("✅ Setup complete!");
  Serial.print("📡 Stream URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println(":81/stream");
  Serial.print("🌐 Upload to: ");
  Serial.println(renderServerUrl + analyzeEndpoint);
}

void loop() {
  server.handleClient();
  
  // Upload image to Render server at intervals
  if (millis() - lastUploadTime > uploadInterval) {
    uploadImageToServer();
    lastUploadTime = millis();
  }
  
  delay(100);
}

void setupWiFi() {
  Serial.print("🔗 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  int attempts = 0;
  
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("📡 ESP IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    // Continue anyway, will try to reconnect
  }
}

void setupCamera() {
  Serial.println("📷 Initializing camera...");
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
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
  config.frame_size   = FRAMESIZE_QVGA;  // 320x240
  config.jpeg_quality = 12;  // Good quality
  config.fb_count     = 1;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x\n", err);
    return;
  }
  
  Serial.println("✅ Camera initialized successfully");
}

void setupWebServer() {
  // MJPEG streaming endpoint
  server.on("/stream", HTTP_GET, []() {
    WiFiClient client = server.client();
    String response = "HTTP/1.1 200 OK\r\n"
                     "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n"
                     "Access-Control-Allow-Origin: *\r\n"
                     "\r\n--frame\r\n";
    server.sendContent(response);

    while (client.connected()) {
      camera_fb_t* fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("❌ Camera capture failed");
        continue;
      }
      
      response = "Content-Type: image/jpeg\r\nContent-Length: " + String(fb->len) + "\r\n\r\n";
      server.sendContent(response);
      server.sendContent_P((const char*)fb->buf, fb->len);
      server.sendContent("\r\n--frame\r\n");
      esp_camera_fb_return(fb);
      
      delay(30);  // ~30 FPS
    }
  });
  
  // Status endpoint
  server.on("/status", HTTP_GET, []() {
    String status = "{";
    status += "\"wifi_connected\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false") + ",";
    status += "\"ip_address\":\"" + WiFi.localIP().toString() + "\",";
    status += "\"render_server\":\"" + renderServerUrl + "\",";
    status += "\"uptime\":" + String(millis()) + "";
    status += "}";
    server.send(200, "application/json", status);
  });
  
  server.begin();
  Serial.println("🌐 Web server started on port 81");
}

bool uploadImageToServer() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected - skipping upload");
    setupWiFi();  // Try to reconnect
    return false;
  }
  
  Serial.println("📤 Capturing and uploading image...");
  
  // Capture image
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Camera capture failed");
    return false;
  }
  
  // Upload with retry logic
  bool success = false;
  for (int attempt = 1; attempt <= maxRetries; attempt++) {
    success = attemptUpload(fb, attempt);
    if (success) break;
    
    if (attempt < maxRetries) {
      Serial.printf("⏳ Retrying in %d seconds... (attempt %d/%d)\n", retryDelay/1000, attempt, maxRetries);
      delay(retryDelay);
    }
  }
  
  esp_camera_fb_return(fb);
  return success;
}

bool attemptUpload(camera_fb_t* fb, int attempt) {
  HTTPClient http;
  String url = renderServerUrl + analyzeEndpoint;
  
  Serial.printf("📡 Upload attempt %d/%d to: %s\n", attempt, maxRetries, url.c_str());
  
  if (!http.begin(url)) {
    Serial.println("❌ HTTP client failed to begin");
    return false;
  }
  
  http.addHeader("Content-Type", "image/jpeg");
  http.addHeader("User-Agent", "ESP32-Camera/1.0");
  http.setTimeout(15000);  // 15 second timeout
  
  int httpCode = http.POST(fb->buf, fb->len);
  String payload = http.getString();
  
  bool success = (httpCode >= 200 && httpCode < 300);
  
  if (success) {
    Serial.printf("✅ Upload successful! Code: %d\n", httpCode);
    if (payload.length() > 0) {
      Serial.print("📄 Response: ");
      Serial.println(payload);
    }
  } else {
    Serial.printf("❌ Upload failed! Code: %d, Error: %s\n", httpCode, payload.c_str());
  }
  
  http.end();
  return success;
}
