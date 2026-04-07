#!/usr/bin/env python3
"""
Simple credential test script
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Checking Environment Variables...")
print("=" * 50)

# MongoDB
MONGODB_URI = os.environ.get('MONGODB_URI', '')
print(f"📊 MongoDB URI: {MONGODB_URI[:50]}..." if MONGODB_URI else "❌ MongoDB URI not set")

# Email
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
EMAIL_TO = os.environ.get('EMAIL_TO', '')

print(f"📧 Email User: {EMAIL_USER}")
print(f"📬 Email To: {EMAIL_TO}")
print(f"🔑 Email Pass: {'*' * len(EMAIL_PASS) if EMAIL_PASS else 'NOT SET'} ({len(EMAIL_PASS)} chars)")

print("\n🧪 Testing MongoDB Connection...")
try:
    from pymongo import MongoClient
    
    # Try different connection string formats
    test_uri = "mongodb+srv://nithishkumarmb775_db_user:SH5opjXilokse2pJ@cluster0.mongodb.net/?retryWrites=true&w=majority"
    
    print(f"🔗 Trying connection: {test_uri[:50]}...")
    client = MongoClient(test_uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # List databases
    dbs = client.list_database_names()
    print(f"📊 Available databases: {dbs}")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

print("\n📧 Testing Email Configuration...")
print("💡 For Gmail app password:")
print("   1. Go to Google Account Settings")
print("   2. Security → 2-Step Verification → App passwords")
print("   3. Generate new password for 'Mail'")
print("   4. Copy 16-character password (no spaces)")
print("   5. Update .env file")

print(f"\n🎯 Current email password length: {len(EMAIL_PASS)} characters")
print("💡 Gmail app passwords are exactly 16 characters")

if len(EMAIL_PASS) != 16:
    print("⚠️ Password length incorrect - should be 16 characters")
else:
    print("✅ Password length looks correct")