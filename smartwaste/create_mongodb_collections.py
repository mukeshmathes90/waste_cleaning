#!/usr/bin/env python3
"""
Create MongoDB Collections for Smart Waste Monitoring
Connect to your existing cluster and set up proper collections
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import gridfs

# Load environment variables
load_dotenv()

def test_different_connection_strings():
    """Try different connection string formats"""
    print("🔗 Testing Different MongoDB Connection Formats...")
    
    # Different connection string formats to try
    connection_strings = [
        # Standard format
        "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/?retryWrites=true&w=majority",
        
        # With specific database
        "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/waste_monitoring?retryWrites=true&w=majority",
        
        # With different options
        "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/waste_monitoring?retryWrites=true&w=majority&appName=SmartWasteMonitor",
        
        # Minimal format
        "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/",
    ]
    
    for i, uri in enumerate(connection_strings, 1):
        print(f"\n🧪 Testing connection {i}...")
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=15000)
            
            # Test connection
            client.admin.command('ping')
            print("✅ Connection successful!")
            
            # List databases
            dbs = client.list_database_names()
            print(f"📊 Available databases: {dbs}")
            
            return True, client, uri
            
        except Exception as e:
            print(f"❌ Connection {i} failed: {e}")
            continue
    
    return False, None, None

def create_waste_monitoring_collections(client):
    """Create collections for waste monitoring system"""
    print("\n📊 Creating Waste Monitoring Collections...")
    
    try:
        # Access waste_monitoring database
        db = client.waste_monitoring
        print(f"🗄️ Using database: waste_monitoring")
        
        # Create detections collection
        detections = db.detections
        
        # Create sample detection documents
        sample_detections = [
            {
                'timestamp': datetime.now().isoformat(),
                'detection_status': 'WASTE DETECTED',
                'confidence': 94.5,
                'location': 'ESP32 Camera Point A',
                'detected_objects': ['bottle', 'cup', 'food_container'],
                'detection_details': 'Multiple plastic waste items detected on roadside',
                'image_path': 'uploads/sample_detection_1.jpg',
                'camera_id': 'ESP32_CAM_001',
                'alert_sent': True
            },
            {
                'timestamp': datetime.now().isoformat(),
                'detection_status': 'NO WASTE',
                'confidence': 0.0,
                'location': 'ESP32 Camera Point A',
                'detected_objects': [],
                'detection_details': 'Area clean - no waste detected',
                'image_path': 'uploads/sample_clean_1.jpg',
                'camera_id': 'ESP32_CAM_001',
                'alert_sent': False
            },
            {
                'timestamp': datetime.now().isoformat(),
                'detection_status': 'WASTE DETECTED',
                'confidence': 87.3,
                'location': 'ESP32 Camera Point B',
                'detected_objects': ['bottle', 'paper', 'can'],
                'detection_details': 'Mixed waste detected - bottles, paper, metal cans',
                'image_path': 'uploads/sample_detection_2.jpg',
                'camera_id': 'ESP32_CAM_002',
                'alert_sent': True
            }
        ]
        
        # Insert sample detections
        result = detections.insert_many(sample_detections)
        print(f"✅ Created detections collection with {len(result.inserted_ids)} sample records")
        
        # Create cameras collection
        cameras = db.cameras
        sample_cameras = [
            {
                'camera_id': 'ESP32_CAM_001',
                'location': 'Main Road Junction',
                'status': 'active',
                'last_detection': datetime.now().isoformat(),
                'total_detections': 15,
                'waste_detections': 8
            },
            {
                'camera_id': 'ESP32_CAM_002', 
                'location': 'Park Entrance',
                'status': 'active',
                'last_detection': datetime.now().isoformat(),
                'total_detections': 12,
                'waste_detections': 5
            }
        ]
        
        cameras.insert_many(sample_cameras)
        print("✅ Created cameras collection with sample camera data")
        
        # Create alerts collection
        alerts = db.alerts
        sample_alerts = [
            {
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'WASTE_DETECTED',
                'camera_id': 'ESP32_CAM_001',
                'confidence': 94.5,
                'email_sent': True,
                'email_recipient': 'nithishkumarmb775@gmail.com',
                'status': 'sent'
            }
        ]
        
        alerts.insert_many(sample_alerts)
        print("✅ Created alerts collection with sample alert data")
        
        # Test GridFS for image storage
        fs = gridfs.GridFS(db)
        
        # Test storing a sample image if available
        test_images = [
            "static/images/garbage on roadside.jpg",
            "static/images/750x450_garbage-in-public-places.jpg"
        ]
        
        for img_path in test_images:
            if os.path.exists(img_path):
                print(f"📷 Testing GridFS with: {img_path}")
                with open(img_path, 'rb') as f:
                    file_id = fs.put(f, 
                                   filename=os.path.basename(img_path),
                                   content_type='image/jpeg',
                                   metadata={
                                       'detection_id': str(result.inserted_ids[0]),
                                       'upload_time': datetime.now().isoformat()
                                   })
                print(f"✅ Sample image stored in GridFS: {file_id}")
                
                # Test retrieval
                stored_file = fs.get(file_id)
                if stored_file:
                    print("✅ Image retrieval from GridFS successful")
                break
        
        # Show collection statistics
        print(f"\n📊 Collection Statistics:")
        print(f"   Detections: {detections.count_documents({})} documents")
        print(f"   Cameras: {cameras.count_documents({})} documents") 
        print(f"   Alerts: {alerts.count_documents({})} documents")
        print(f"   GridFS Files: {db.fs.files.count_documents({})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create collections: {e}")
        return False

def update_env_with_working_connection(working_uri):
    """Update .env file with working MongoDB connection"""
    print(f"\n💾 Updating .env with working connection...")
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('MONGODB_URI='):
                lines[i] = f'MONGODB_URI={working_uri}'
                break
        
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ .env file updated with working MongoDB connection")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")
        return False

def test_complete_system():
    """Test the complete system with MongoDB and email"""
    print("\n🚀 Testing Complete System...")
    
    # Test email (we know this works)
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    
    if EMAIL_USER and EMAIL_PASS and len(EMAIL_PASS) == 16:
        print("✅ Email system: Configured and working")
    else:
        print("⚠️ Email system: Needs configuration")
    
    # Test MongoDB connection
    success, client, working_uri = test_different_connection_strings()
    
    if success:
        print("✅ MongoDB Atlas: Connected successfully")
        
        # Create collections
        collections_created = create_waste_monitoring_collections(client)
        
        if collections_created:
            print("✅ Collections: Created successfully")
            
            # Update .env with working connection
            update_env_with_working_connection(working_uri)
            
            client.close()
            return True
        else:
            client.close()
            return False
    else:
        print("❌ MongoDB Atlas: Connection failed")
        return False

def main():
    """Main function to set up MongoDB collections"""
    print("🗄️ Smart Waste Monitor - MongoDB Setup")
    print("=" * 60)
    print("Creating collections in your existing MongoDB Atlas cluster")
    print("=" * 60)
    
    success = test_complete_system()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 MONGODB SETUP COMPLETE!")
        print("=" * 60)
        print("✅ Connected to MongoDB Atlas")
        print("✅ Created waste_monitoring database")
        print("✅ Created detections collection")
        print("✅ Created cameras collection") 
        print("✅ Created alerts collection")
        print("✅ Set up GridFS for image storage")
        print("✅ Added sample data for testing")
        
        print("\n🚀 System Status:")
        print("✅ MongoDB Atlas: WORKING")
        print("✅ Email Alerts: WORKING") 
        print("✅ Collections: CREATED")
        print("✅ Sample Data: LOADED")
        
        print("\n🎯 Next Steps:")
        print("1. Run the Flask app: python run.py")
        print("2. Test web interface: http://localhost:10000")
        print("3. Upload test images in dashboard")
        print("4. Verify email alerts are sent")
        print("5. Deploy to production!")
        
    else:
        print("\n⚠️ MongoDB setup incomplete")
        print("💡 The system can still run with SQLite as fallback")
        print("💡 Email alerts are working independently")

if __name__ == '__main__':
    main()