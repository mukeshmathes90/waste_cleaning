from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import cv2
import numpy as np
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
from werkzeug.utils import secure_filename
import base64
from ultralytics import YOLO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Security: Use environment variables for sensitive data
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Email configuration from environment variables
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
EMAIL_TO = os.environ.get('EMAIL_TO', 'municipal@city.gov')

# User credentials from environment variables (NO SIGNUP)
users = {
    "admin": os.environ.get('ADMIN_PASSWORD', 'admin123'),
    "officer": os.environ.get('OFFICER_PASSWORD', 'waste2026')
}

# Initialize YOLO model
try:
    model = YOLO("yolov8n.pt")
except:
    model = None
    print("YOLO model not found. Please ensure yolov8n.pt is in the project directory.")

# Database initialization
def init_db():
    conn = sqlite3.connect('waste_monitoring.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS detections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  image_path TEXT,
                  detection_status TEXT,
                  confidence REAL,
                  location TEXT)''')
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email_alert(image_path, detection_confidence):
    """Send email alert for waste detection"""
    try:
        # Skip email if credentials not configured
        if not EMAIL_USER or not EMAIL_PASS:
            print(f"Email alert skipped - credentials not configured. Detection: {detection_confidence:.2f}%")
            return True
            
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🚨 Waste Detected - Smart Monitoring Alert"
        
        body = f"""
        WASTE DETECTION ALERT 🚨
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Confidence: {detection_confidence:.2f}%
        Location: Roadside Monitoring Point
        
        Please take immediate action for waste collection.
        
        Smart Waste Monitoring System
        AI for Cleaner Cities 🌱
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach image
        with open(image_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= detected_waste.jpg'
            )
            msg.attach(part)
        
        # Send email via SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_TO, text)
        server.quit()
        
        print(f"Email alert sent successfully for detection: {detection_confidence:.2f}%")
        return True
        
    except Exception as e:
        print(f"Email error: {e}")
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
    
    # Get recent detections from database
    conn = sqlite3.connect('waste_monitoring.db')
    c = conn.cursor()
    c.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10')
    detections = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', detections=detections, user=session['user'])

@app.route('/upload', methods=['POST'])
def upload_image():
    """ESP32 compatible upload endpoint - redirects to analyze"""
    return analyze_image()

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Handle image analysis from ESP32 (raw JPEG) or web form (multipart)"""
    try:
        filepath = None
        
        # Handle ESP32 raw JPEG data
        if request.data:
            # ESP32 sends raw JPEG bytes
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_esp32.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save raw JPEG data
            with open(filepath, "wb") as f:
                f.write(request.data)
                
        # Handle web form multipart data (for dashboard testing)
        elif 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image selected'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
            else:
                return jsonify({'error': 'Invalid file type'}), 400
        else:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Run YOLO detection on saved image
        waste_detected = False
        confidence = 0.0
        
        if model and filepath:
            results = model(filepath)
            
            # Check for waste-related objects (bottles, cups, trash, etc.)
            waste_classes = ['bottle', 'cup', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot']
            
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
        
        # Store detection in database
        conn = sqlite3.connect('waste_monitoring.db')
        c = conn.cursor()
        c.execute('INSERT INTO detections (timestamp, image_path, detection_status, confidence, location) VALUES (?, ?, ?, ?, ?)',
                 (datetime.now().isoformat(), filepath, 
                  'WASTE DETECTED' if waste_detected else 'NO WASTE', 
                  confidence, 'ESP32 Camera Point'))
        conn.commit()
        conn.close()
        
        # Send email alert if waste detected
        if waste_detected:
            send_email_alert(filepath, confidence)
        
        return jsonify({
            'success': True,
            'waste_detected': waste_detected,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'image_path': filepath
        })
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/detections')
def get_detections():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('waste_monitoring.db')
    c = conn.cursor()
    c.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT 20')
    detections = c.fetchall()
    conn.close()
    
    detection_list = []
    for detection in detections:
        detection_list.append({
            'id': detection[0],
            'timestamp': detection[1],
            'image_path': detection[2],
            'status': detection[3],
            'confidence': detection[4],
            'location': detection[5]
        })
    
    return jsonify(detection_list)

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)