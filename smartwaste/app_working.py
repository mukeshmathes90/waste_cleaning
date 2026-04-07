from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import os
import cv2
import numpy as np
from datetime import datetime
import threading
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
import base64
from ultralytics import YOLO
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Security: Use environment variables for sensitive data
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Render compatibility - get port from environment or default to 10000
PORT = int(os.environ.get('PORT', 10000))

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Email configuration from environment variables
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
EMAIL_TO = os.environ.get('EMAIL_TO', 'municipal@city.gov')

# MongoDB configuration
MONGODB_URI = os.environ.get('MONGODB_URI', '')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'waste_monitoring')

# User credentials from environment variables (NO SIGNUP)
users = {
    "admin": os.environ.get('ADMIN_PASSWORD', 'admin123'),
    "officer": os.environ.get('OFFICER_PASSWORD', 'waste2026')
}

# ESP32-CAM live stream URL (set in .env for officer dashboard)
ESP_CAM_STREAM_URL = os.environ.get('ESP_CAM_STREAM_URL', '')
# Use webcam as fallback if no ESP32 URL is configured
USE_WEBCAM_FALLBACK = os.environ.get('USE_WEBCAM_FALLBACK', 'true').lower() == 'true'
WEBCAM_INDEX = int(os.environ.get('WEBCAM_INDEX', '0'))  # Default webcam device index

# Location Configuration - Specific address for Erode
ESP_CAM_LOCATION = os.environ.get('ESP_CAM_LOCATION', '2nd Cross Street, Vinayaka Nagar, Erode - 638001')
ESP_CAM_SHORT_LOCATION = os.environ.get('ESP_CAM_SHORT_LOCATION', '2nd Cross Street, Erode')
ESP_CAM_FULL_ADDRESS = os.environ.get('ESP_CAM_FULL_ADDRESS', '2nd Cross Street, Vinayaka Nagar, Erode, Tamil Nadu - 638001')

# YOLO Detection Settings
LIVE_YOLO_FPS = float(os.environ.get('LIVE_YOLO_FPS', '2'))  # dashboard refresh / worker frame rate target
LIVE_YOLO_DETECT_EVERY_SEC = float(os.environ.get('LIVE_YOLO_DETECT_EVERY_SEC', '2'))  # run YOLO at most every N seconds
LIVE_YOLO_MIN_CONF = float(os.environ.get('LIVE_YOLO_MIN_CONF', '0.3'))
LIVE_YOLO_EMAIL_COOLDOWN_SEC = int(os.environ.get('LIVE_YOLO_EMAIL_COOLDOWN_SEC', '60'))

# Latest live frames (JPEG bytes)
_live_lock = threading.Lock()
_live_raw_jpeg = None
_live_yolo_jpeg = None
_live_last_frame_ts = 0.0
_live_last_detection_ts = 0.0
_live_last_email_ts = 0.0
_live_worker_started = False

# Initialize MongoDB connection
try:
    if MONGODB_URI:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        db = client[DATABASE_NAME]
        detections_collection = db.detections
        fs = gridfs.GridFS(db)  # For storing images
        print("✅ MongoDB Atlas connected successfully")
        USE_MONGODB = True
    else:
        raise Exception("MongoDB URI not configured")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("📊 Falling back to SQLite database")
    client = None
    db = None
    detections_collection = None
    fs = None
    USE_MONGODB = False
    
    # Initialize SQLite as fallback
    import sqlite3
    def init_sqlite_db():
        conn = sqlite3.connect('waste_monitoring.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS detections
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT,
                      image_path TEXT,
                      detection_status TEXT,
                      confidence REAL,
                      location TEXT,
                      detected_objects TEXT,
                      detection_details TEXT)''')
        conn.commit()
        conn.close()
    
    init_sqlite_db()

# Initialize YOLO model
try:
    model = YOLO("yolov8n.pt")
    print("✅ YOLO model loaded successfully")
except Exception as e:
    model = None
    print(f"❌ YOLO model loading failed: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _normalize_path(p: str) -> str:
    # convert backslashes -> forward slashes and strip any leading slash
    # so that paths like "/static/images/foo.jpg" are treated the same as
    # "static/images/foo.jpg". This makes the dashboard logic properly
    # detect static resources and avoid routing them through `/image/` which
    # only serves files from the uploads folder.
    return (p or "").replace("\\", "/").lstrip("/")

def _encode_jpeg_bgr(frame_bgr, quality=80):
    try:
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
        ok, buf = cv2.imencode(".jpg", frame_bgr, encode_params)
        if not ok:
            return None
        return buf.tobytes()
    except Exception:
        return None

def _save_detection_image_bytes(image_bytes, prefix="live_yolo"):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{prefix}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    return filepath

def _is_waste_class(name: str) -> bool:
    waste_classes = {
        'bottle', 'cup', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
        'broccoli', 'carrot', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
        'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven',
        'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
        'teddy bear', 'hair drier', 'toothbrush'
    }
    return (name or "").lower() in waste_classes

def _run_yolo_on_frame(frame_bgr):
    """Run YOLO on a BGR frame. Returns: (waste_detected, confidence_pct, detected_objects_list, details_str, annotated_bgr)"""
    if model is None:
        return False, 0.0, [], "YOLO model not loaded", frame_bgr

    waste_detected = False
    confidence_pct = 0.0
    detected_objects = []

    results = model(frame_bgr)
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = model.names.get(class_id, str(class_id))
                conf = float(box.conf[0])
                if _is_waste_class(class_name) and conf >= LIVE_YOLO_MIN_CONF:
                    waste_detected = True
                    confidence_pct = max(confidence_pct, conf * 100)
                    detected_objects.append(f"{class_name} ({conf*100:.1f}%)")

    detection_details = "No waste detected"
    if detected_objects:
        detection_details = f"Detected objects: {', '.join(detected_objects)}"

    # Annotated frame from ultralytics
    try:
        annotated = results[0].plot()
    except Exception:
        annotated = frame_bgr

    return waste_detected, confidence_pct, detected_objects, detection_details, annotated

def _live_camera_worker():
    global _live_raw_jpeg, _live_yolo_jpeg, _live_last_frame_ts, _live_last_detection_ts, _live_last_email_ts

    if not ESP_CAM_STREAM_URL:
        print("⚠️ Live camera worker not started - ESP_CAM_STREAM_URL not set")
        return

    print(f"📡 Starting live camera worker using: {ESP_CAM_STREAM_URL}")
    cap = None
    backoff = 1.0

    while True:
        try:
            if cap is None or not cap.isOpened():
                print(f"🔄 Attempting to connect to ESP32 stream: {ESP_CAM_STREAM_URL}")
                cap = cv2.VideoCapture(ESP_CAM_STREAM_URL)
                # Set timeout and buffer size for better streaming
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FPS, 10)
                # Some backends need a moment
                time.sleep(0.5)
                
                if not cap.isOpened():
                    raise RuntimeError(f"Failed to open stream: {ESP_CAM_STREAM_URL}")
                
                print("✅ ESP32 stream connected successfully")

            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError("Failed to read frame from ESP32 stream")

            now = time.time()
            raw_jpeg = _encode_jpeg_bgr(frame, quality=75)
            if raw_jpeg:
                with _live_lock:
                    _live_raw_jpeg = raw_jpeg
                    _live_last_frame_ts = now

            # Run YOLO only every N seconds to keep CPU stable
            if (now - _live_last_detection_ts) >= LIVE_YOLO_DETECT_EVERY_SEC:
                waste_detected, conf_pct, objs, details, annotated = _run_yolo_on_frame(frame)
                yolo_jpeg = _encode_jpeg_bgr(annotated, quality=80)
                if yolo_jpeg:
                    with _live_lock:
                        _live_yolo_jpeg = yolo_jpeg
                        _live_last_detection_ts = now

                # If waste detected, snapshot (annotated) and store + email (cooldown protected)
                if waste_detected and yolo_jpeg and (now - _live_last_email_ts) >= LIVE_YOLO_EMAIL_COOLDOWN_SEC:
                    try:
                        filepath = _save_detection_image_bytes(yolo_jpeg, prefix="live_yolo_detected")
                        image_id = store_image_in_mongodb(filepath)

                        if USE_MONGODB and detections_collection:
                            detection_doc = {
                                'timestamp': datetime.now().isoformat(),
                                'image_path': filepath,
                                'image_id': image_id,
                                'detection_status': 'WASTE DETECTED',
                                'confidence': conf_pct,
                                'location': ESP_CAM_LOCATION,
                                'detected_objects': objs,
                                'detection_details': details,
                                'source': 'LIVE_STREAM'
                            }
                            detections_collection.insert_one(detection_doc)
                        else:
                            import sqlite3
                            conn = sqlite3.connect('waste_monitoring.db')
                            c = conn.cursor()
                            c.execute('''INSERT INTO detections 
                                       (timestamp, image_path, detection_status, confidence, location, detected_objects, detection_details) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                     (datetime.now().isoformat(), filepath,
                                      'WASTE DETECTED',
                                      conf_pct, ESP_CAM_LOCATION,
                                      ', '.join(objs), details))
                            conn.commit()
                            conn.close()

                        send_email_alert_with_image(filepath, conf_pct, details)
                        _live_last_email_ts = now
                        print(f"🚨 Live waste detected. Stored + emailed. Confidence: {conf_pct:.1f}%")
                    except Exception as e:
                        print(f"❌ Live detection store/email failed: {e}")

            # Pace loop roughly to target FPS (best-effort)
            if LIVE_YOLO_FPS > 0:
                time.sleep(max(0.0, (1.0 / LIVE_YOLO_FPS) - 0.001))
            backoff = 1.0
        except Exception as e:
            try:
                if cap is not None:
                    cap.release()
            except Exception:
                pass
            cap = None
            print(f"⚠️ Live camera worker error: {e}. Retrying in {backoff:.1f}s")
            time.sleep(backoff)
            backoff = min(backoff * 2.0, 10.0)

def _webcam_worker():
    """Webcam fallback worker - captures frames from local webcam and runs YOLO detection"""
    global _live_raw_jpeg, _live_yolo_jpeg, _live_last_frame_ts, _live_last_detection_ts, _live_last_email_ts

    if not USE_WEBCAM_FALLBACK:
        print("⚠️ Webcam fallback disabled")
        return

    print(f"📷 Starting webcam worker (device index: {WEBCAM_INDEX})")
    cap = None
    backoff = 1.0

    while True:
        try:
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(WEBCAM_INDEX)
                if not cap.isOpened():
                    raise RuntimeError(f"Cannot open webcam device {WEBCAM_INDEX}")
                # Set resolution for better performance
                cap.set(3, 640)  # Width
                cap.set(4, 480)  # Height
                print(f"✅ Webcam opened successfully")
                time.sleep(0.5)

            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError("Failed to read frame from webcam")

            now = time.time()
            raw_jpeg = _encode_jpeg_bgr(frame, quality=75)
            if raw_jpeg:
                with _live_lock:
                    _live_raw_jpeg = raw_jpeg
                    _live_last_frame_ts = now

            # Run YOLO only every N seconds to keep CPU stable
            if (now - _live_last_detection_ts) >= LIVE_YOLO_DETECT_EVERY_SEC:
                waste_detected, conf_pct, objs, details, annotated = _run_yolo_on_frame(frame)
                yolo_jpeg = _encode_jpeg_bgr(annotated, quality=80)
                if yolo_jpeg:
                    with _live_lock:
                        _live_yolo_jpeg = yolo_jpeg
                        _live_last_detection_ts = now

                # If waste detected, snapshot (annotated) and store + email (cooldown protected)
                if waste_detected and yolo_jpeg and (now - _live_last_email_ts) >= LIVE_YOLO_EMAIL_COOLDOWN_SEC:
                    try:
                        filepath = _save_detection_image_bytes(yolo_jpeg, prefix="webcam_yolo_detected")
                        image_id = store_image_in_mongodb(filepath)

                        if USE_MONGODB and detections_collection:
                            detection_doc = {
                                'timestamp': datetime.now().isoformat(),
                                'image_path': filepath,
                                'image_id': image_id,
                                'detection_status': 'WASTE DETECTED',
                                'confidence': conf_pct,
                                'location': 'Webcam - Local Camera',
                                'detected_objects': objs,
                                'detection_details': details,
                                'source': 'WEBCAM'
                            }
                            detections_collection.insert_one(detection_doc)
                        else:
                            import sqlite3
                            conn = sqlite3.connect('waste_monitoring.db')
                            c = conn.cursor()
                            c.execute('''INSERT INTO detections 
                                       (timestamp, image_path, detection_status, confidence, location, detected_objects, detection_details) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                     (datetime.now().isoformat(), filepath,
                                      'WASTE DETECTED',
                                      conf_pct, 'Webcam - Local Camera',
                                      ', '.join(objs), details))
                            conn.commit()
                            conn.close()

                        send_email_alert_with_image(filepath, conf_pct, details)
                        _live_last_email_ts = now
                        print(f"🚨 Webcam waste detected. Stored + emailed. Confidence: {conf_pct:.1f}%")
                    except Exception as e:
                        print(f"❌ Webcam detection store/email failed: {e}")

            # Pace loop roughly to target FPS (best-effort)
            if LIVE_YOLO_FPS > 0:
                time.sleep(max(0.0, (1.0 / LIVE_YOLO_FPS) - 0.001))
            backoff = 1.0
        except Exception as e:
            try:
                if cap is not None:
                    cap.release()
            except Exception:
                pass
            cap = None
            print(f"⚠️ Webcam worker error: {e}. Retrying in {backoff:.1f}s")
            time.sleep(backoff)
            backoff = min(backoff * 2.0, 10.0)

def _ensure_live_worker_started():
    global _live_worker_started
    if _live_worker_started:
        return
    
    # Start ESP32 worker if URL is configured
    if ESP_CAM_STREAM_URL:
        t = threading.Thread(target=_live_camera_worker, daemon=True)
        t.start()
        _live_worker_started = True
        return
    
    # Start webcam fallback if enabled and no ESP32 URL
    if USE_WEBCAM_FALLBACK:
        t = threading.Thread(target=_webcam_worker, daemon=True)
        t.start()
        _live_worker_started = True
        return

def store_image_in_mongodb(image_path):
    """Store image in MongoDB GridFS and return file ID"""
    try:
        if fs and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                file_id = fs.put(f, filename=os.path.basename(image_path))
            return str(file_id)
    except Exception as e:
        print(f"Error storing image in MongoDB: {e}")
    return None

def get_image_from_mongodb(file_id):
    """Retrieve image from MongoDB GridFS"""
    try:
        if fs and file_id:
            return fs.get(ObjectId(file_id))
    except Exception as e:
        print(f"Error retrieving image from MongoDB: {e}")
    return None

def send_email_alert_with_image(image_path, detection_confidence, detection_details=None):
    """Send email alert with image attachment for waste detection"""
    try:
        # Skip email if credentials not configured
        if not EMAIL_USER or not EMAIL_PASS:
            print(f"📧 Email alert skipped - credentials not configured. Detection: {detection_confidence:.2f}%")
            return True
            
        print(f"📧 Preparing email alert for detection: {detection_confidence:.2f}%")
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🚨 Waste Detected - Smart Monitoring Alert"
        
        # Enhanced email body with detection details
        body = f"""
🚨 WASTE DETECTION ALERT 🚨

📅 Detection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Confidence Level: {detection_confidence:.2f}%
📍 Location: {ESP_CAM_FULL_ADDRESS}
📍 Short Location: {ESP_CAM_SHORT_LOCATION}
🤖 AI System: YOLO Object Detection

📊 DETECTION DETAILS:
{detection_details if detection_details else 'Waste objects detected in the monitored area'}

⚡ IMMEDIATE ACTION REQUIRED:
1. Dispatch waste collection team to: {ESP_CAM_SHORT_LOCATION}
2. Update collection status in the dashboard
3. Monitor for recurring waste accumulation at this location

🗺️ DETAILED ADDRESS:
{ESP_CAM_FULL_ADDRESS}

🌐 System Dashboard: 
   Access your monitoring dashboard for more details and images

📷 ATTACHED IMAGE:
   High-resolution image of the detected waste is attached to this email

Smart Waste Monitoring System
🤖 AI-Powered | 📷 ESP32 Cameras | ☁️ Cloud Monitoring
AI for Cleaner Cities 🌱

---
This is an automated alert from your Smart Waste Monitoring System.
For technical support, check the system dashboard or logs.
Location: {ESP_CAM_SHORT_LOCATION}, Erode
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach image if it exists
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    
                    # Get filename for attachment
                    filename = os.path.basename(image_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= waste_detected_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
                    )
                    msg.attach(part)
                    print(f"📎 Image attached: {filename}")
            except Exception as e:
                print(f"⚠️ Failed to attach image: {e}")
        
        # Send email via Gmail SMTP
        print("📡 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Authenticating with Gmail...")
        server.login(EMAIL_USER, EMAIL_PASS)
        
        print("📤 Sending email alert...")
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_TO, text)
        server.quit()
        
        print(f"✅ Email alert sent successfully to {EMAIL_TO}")
        print(f"📧 Detection confidence: {detection_confidence:.2f}%")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Email authentication failed: {e}")
        print("💡 Check Gmail app password and 2FA settings")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

@app.route('/')
def home():
    # Get sample images for gallery
    image_files = []
    static_images_path = os.path.join('static', 'images')
    if os.path.exists(static_images_path):
        for file in os.listdir(static_images_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.avif')):
                image_files.append(file)
    
    return render_template('home.html', sample_images=image_files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    _ensure_live_worker_started()
    
    # Get recent detections from database (MongoDB or SQLite)
    detections = []
    try:
        if USE_MONGODB and detections_collection:
            # Get from MongoDB
            cursor = detections_collection.find().sort('timestamp', -1).limit(10)
            for doc in cursor:
                image_path = doc.get('image_path', '')
                norm = _normalize_path(image_path)
                image_is_static = norm.startswith("static/")
                static_filename = norm[len("static/"):] if image_is_static else ""
                detections.append({
                    'id': str(doc['_id']),
                    'timestamp': doc.get('timestamp', ''),
                    'detection_status': doc.get('detection_status', ''),
                    'confidence': doc.get('confidence', 0),
                    'location': doc.get('location', ''),
                    'image_id': doc.get('image_id', ''),
                    'image_path': image_path,
                    'image_filename': os.path.basename(image_path) if image_path else '',
                    'image_is_static': image_is_static,
                    'static_filename': static_filename,
                })
        else:
            # Get from SQLite
            import sqlite3
            conn = sqlite3.connect('waste_monitoring.db')
            c = conn.cursor()
            c.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10')
            rows = c.fetchall()
            conn.close()
            
            for row in rows:
                image_path = row[2]
                norm = _normalize_path(image_path)
                image_is_static = norm.startswith("static/")
                static_filename = norm[len("static/"):] if image_is_static else ""
                detections.append({
                    'id': str(row[0]),
                    'timestamp': row[1],
                    'detection_status': row[3],
                    'confidence': row[4],
                    'location': row[5],
                    'image_path': image_path,
                    'image_filename': os.path.basename(image_path) if image_path else '',
                    'image_is_static': image_is_static,
                    'static_filename': static_filename,
                    'detected_objects': row[6] if len(row) > 6 and row[6] else [],
                    'detection_details': row[7] if len(row) > 7 else ''
                })
    except Exception as e:
        print(f"Error fetching detections: {e}")
    
    # Debug: log configured ESP stream URL so we can confirm load_dotenv worked
    try:
        print(f"DEBUG: ESP_CAM_STREAM_URL='{ESP_CAM_STREAM_URL}'")
    except Exception:
        pass

    return render_template('dashboard.html', detections=detections, user=session['user'], esp_stream_url=ESP_CAM_STREAM_URL, use_webcam_fallback=USE_WEBCAM_FALLBACK)

@app.route('/live/yolo.jpg')
def live_yolo_jpg():
    if 'user' not in session:
        return "Unauthorized", 401
    _ensure_live_worker_started()
    with _live_lock:
        data = _live_yolo_jpeg or _live_raw_jpeg
    if not data:
        return "No frame yet", 404
    return Response(data, mimetype='image/jpeg', headers={'Cache-Control': 'no-store'})

@app.route('/live/status')
def live_status():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    with _live_lock:
        return jsonify({
            'stream_url_configured': bool(ESP_CAM_STREAM_URL),
            'last_frame_age_sec': (time.time() - _live_last_frame_ts) if _live_last_frame_ts else None,
            'last_detection_age_sec': (time.time() - _live_last_detection_ts) if _live_last_detection_ts else None,
            'last_email_age_sec': (time.time() - _live_last_email_ts) if _live_last_email_ts else None
        })

@app.route('/live/debug')
def live_debug():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    with _live_lock:
        return jsonify({
            'has_raw': _live_raw_jpeg is not None,
            'raw_len': len(_live_raw_jpeg) if _live_raw_jpeg else 0,
            'has_yolo': _live_yolo_jpeg is not None,
            'yolo_len': len(_live_yolo_jpeg) if _live_yolo_jpeg else 0,
            'last_frame_ts': _live_last_frame_ts,
            'last_detection_ts': _live_last_detection_ts
        })

@app.route('/upload', methods=['POST'])
def upload_image():
    """ESP32 compatible upload endpoint - redirects to analyze"""
    return analyze_image()

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Handle image analysis from ESP32 (raw JPEG) or web form (multipart)"""
    try:
        global _live_raw_jpeg, _live_yolo_jpeg, _live_last_frame_ts, _live_last_detection_ts
        filepath = None
        raw_bytes = None
        
        # Handle ESP32 raw JPEG data
        if request.data:
            try:
                # ESP32 sends raw JPEG bytes
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_esp32.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Save raw JPEG data
                raw_bytes = request.data
                with open(filepath, "wb") as f:
                    f.write(raw_bytes)
                print(f"📷 ESP32 image saved: {filepath}")
            except Exception as e:
                print(f"❌ Error saving ESP32 image: {e}")
                return jsonify({'error': f'Failed to save image: {str(e)}'}), 500
                
        # Handle web form multipart data (for dashboard testing)
        elif 'image' in request.files:
            try:
                file = request.files['image']
                if file.filename == '':
                    return jsonify({'error': 'No image selected'}), 400
                
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    print(f"🌐 Web form image saved: {filepath}")
                else:
                    return jsonify({'error': 'Invalid file type'}), 400
            except Exception as e:
                print(f"❌ Error handling web form upload: {e}")
                return jsonify({'error': f'Failed to process upload: {str(e)}'}), 500
        else:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Run YOLO detection on saved image
        waste_detected = False
        confidence = 0.0
        detection_details = "No waste detected"
        detected_objects = []
        annotated_filepath = None
        
        if model and filepath:
            try:
                print("🤖 Running YOLO detection...")
                results = model(filepath)
                
                # Check for waste-related objects
                waste_classes = ['bottle', 'cup', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 
                               'broccoli', 'carrot', 'pizza', 'donut', 'cake', 'chair', 'couch', 
                               'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 
                               'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 
                               'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 
                               'teddy bear', 'hair drier', 'toothbrush']
            
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            class_id = int(box.cls[0])
                            class_name = model.names[class_id]
                            conf = float(box.conf[0])
                            
                            if class_name.lower() in waste_classes and conf > 0.3:
                                waste_detected = True
                                confidence = max(confidence, conf * 100)
                                detected_objects.append(f"{class_name} ({conf*100:.1f}%)")
            
                if detected_objects:
                    detection_details = f"Detected objects: {', '.join(detected_objects)}"
            
                print(f"🎯 Detection result: {waste_detected}, Confidence: {confidence:.2f}%")

                # Update "Live YOLO View" with latest frame (raw + annotated)
                try:
                    if raw_bytes:
                        with _live_lock:
                            _live_raw_jpeg = raw_bytes
                            _live_last_frame_ts = time.time()
                
                    annotated = results[0].plot()
                    yolo_jpeg = _encode_jpeg_bgr(annotated, quality=80)
                    if yolo_jpeg:
                        with _live_lock:
                            _live_yolo_jpeg = yolo_jpeg
                            _live_last_detection_ts = time.time()
                except Exception as e:
                    print(f"⚠️ Failed to update live YOLO view: {e}")
        
        # Store detection in database ONLY if waste is detected
        if waste_detected:
            # Prefer storing annotated image (what officer sees)
            try:
                if model and filepath:
                    annotated = results[0].plot()
                    annotated_bytes = _encode_jpeg_bgr(annotated, quality=85)
                    if annotated_bytes:
                        annotated_filepath = _save_detection_image_bytes(annotated_bytes, prefix="yolo_annotated")
            except Exception as e:
                print(f"⚠️ Failed to save annotated image: {e}")

            store_path = annotated_filepath or filepath

            # Store image in MongoDB GridFS
            image_id = store_image_in_mongodb(store_path)
            
            if USE_MONGODB and detections_collection:
                # Store in MongoDB
                detection_doc = {
                    'timestamp': datetime.now().isoformat(),
                    'image_path': store_path,
                    'image_id': image_id,
                    'detection_status': 'WASTE DETECTED',
                    'confidence': confidence,
                    'location': ESP_CAM_LOCATION,
                    'detected_objects': detected_objects,
                    'detection_details': detection_details
                }
                
                try:
                    result = detections_collection.insert_one(detection_doc)
                    print(f"📊 Waste detection stored in MongoDB: {result.inserted_id}")
                except Exception as e:
                    print(f"❌ Failed to store in MongoDB: {e}")
            else:
                # Store in SQLite
                try:
                    import sqlite3
                    conn = sqlite3.connect('waste_monitoring.db')
                    c = conn.cursor()
                    c.execute('''INSERT INTO detections 
                               (timestamp, image_path, detection_status, confidence, location, detected_objects, detection_details) 
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                     (datetime.now().isoformat(), store_path, 
                                      'WASTE DETECTED', 
                                      confidence, ESP_CAM_LOCATION,
                                      ', '.join(detected_objects), detection_details))
                    conn.commit()
                    conn.close()
                    print(f"📊 Waste detection stored in SQLite database")
                except Exception as e:
                    print(f"❌ Failed to store in SQLite: {e}")
            
            # Send email alert for waste detection
            print("🚨 Waste detected! Sending email alert...")
            email_sent = send_email_alert_with_image(store_path, confidence, detection_details)
            if email_sent:
                print("✅ Email alert sent successfully")
            else:
                print("❌ Email alert failed")
        else:
            print("✅ No waste detected - not storing in database")
            print("💡 Dashboard will only show actual waste detections")
        
        return jsonify({
            'success': True,
            'waste_detected': waste_detected,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'image_path': annotated_filepath or filepath,
            'detected_objects': detected_objects,
            'detection_details': detection_details
        })
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/detections')
def get_detections():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    detections = []
    try:
        if USE_MONGODB and detections_collection:
            # Get from MongoDB
            cursor = detections_collection.find().sort('timestamp', -1).limit(20)
            for doc in cursor:
                detections.append({
                    'id': str(doc['_id']),
                    'timestamp': doc.get('timestamp', ''),
                    'image_path': doc.get('image_path', ''),
                    'image_id': doc.get('image_id', ''),
                    'status': doc.get('detection_status', ''),
                    'confidence': doc.get('confidence', 0),
                    'location': doc.get('location', ''),
                    'detected_objects': doc.get('detected_objects', []),
                    'detection_details': doc.get('detection_details', '')
                })
        else:
            # Get from SQLite
            import sqlite3
            conn = sqlite3.connect('waste_monitoring.db')
            c = conn.cursor()
            c.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT 20')
            rows = c.fetchall()
            conn.close()
            
            for row in rows:
                detections.append({
                    'id': str(row[0]),
                    'timestamp': row[1],
                    'image_path': row[2],
                    'status': row[3],
                    'confidence': row[4],
                    'location': row[5],
                    'detected_objects': row[6].split(', ') if len(row) > 6 and row[6] else [],
                    'detection_details': row[7] if len(row) > 7 else ''
                })
    except Exception as e:
        print(f"Error fetching detections: {e}")
    
    return jsonify(detections)

@app.route('/image/id/<image_id>')
def serve_image_by_id(image_id):
    """Serve detection image from MongoDB GridFS (for officer/admin dashboard)"""
    if 'user' not in session:
        return "Unauthorized", 401
    try:
        if not fs or not image_id:
            return "Image not found", 404
        grid_out = get_image_from_mongodb(image_id)
        if grid_out is None:
            return "Image not found", 404
        data = grid_out.read()
        return Response(data, mimetype='image/jpeg', headers={'Cache-Control': 'max-age=3600'})
    except Exception as e:
        print(f"Error serving image by id {image_id}: {e}")
        return "Image not found", 404

@app.route('/image/<path:filename>')
def serve_image(filename):
    """Serve uploaded images from uploads folder (for SQLite or local files)"""
    try:
        from flask import send_from_directory
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        return "Image not found", 404

@app.route('/test-email')
def test_email_route():
    """Test endpoint for email functionality"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Test email with a sample image
    sample_image = None
    for img in ['static/images/garbage on roadside.jpg', 'static/images/750x450_garbage-in-public-places.jpg']:
        if os.path.exists(img):
            sample_image = img
            break
    
    if sample_image:
        success = send_email_alert_with_image(sample_image, 85.5, "Test detection: Sample waste objects found")
        return jsonify({
            'success': success,
            'message': 'Test email sent' if success else 'Email test failed',
            'email_to': EMAIL_TO
        })
    else:
        return jsonify({'error': 'No sample image found for testing'}), 400

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'yolo_model': 'loaded' if model else 'not_loaded',
        'esp_stream': 'configured' if ESP_CAM_STREAM_URL else 'not_configured'
    })

@app.route('/config')
def get_config():
    """Get configuration for ESP32 setup"""
    return jsonify({
        'esp_stream_url': ESP_CAM_STREAM_URL,
        'analyze_endpoint': '/analyze',
        'stream_endpoint': '/stream',
        'server_url': request.host_url.rstrip('/')
    })

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Test MongoDB connection
    if client:
        try:
            client.admin.command('ping')
            print("✅ MongoDB connection verified")
        except Exception as e:
            print(f"❌ MongoDB ping failed: {e}")
    
    # Start live YOLO worker for stream processing if configured
    print(f"\n🔍 ESP_CAM_STREAM_URL is: {ESP_CAM_STREAM_URL or 'NOT SET'}")
    if ESP_CAM_STREAM_URL:
        print(f"📡 Starting live YOLO worker to process ESP32 stream...")
        _ensure_live_worker_started()
        print(f"✅ Live worker thread started (daemon mode)")
    elif USE_WEBCAM_FALLBACK:
        print(f"📷 Starting webcam fallback worker...")
        _ensure_live_worker_started()
        print(f"✅ Webcam worker started (daemon mode)")
    else:
        print(f"⚠️  No camera configured - live stream disabled")
    
    # Run app
    print(f"\n🚀 Starting Flask server on http://0.0.0.0:{PORT}")
    print(f"🌐 Health check: http://0.0.0.0:{PORT}/health")
    print(f"⚙️  Config endpoint: http://0.0.0.0:{PORT}/config")
    app.run(host='0.0.0.0', port=PORT, debug=False)
