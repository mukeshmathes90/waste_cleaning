#!/usr/bin/env python3
"""
Smart Waste Monitoring System - Startup Script
Run this file to start the application locally
"""

import os
import sys
from app import app, prompt_and_apply_esp_stream

if __name__ == '__main__':
    prompt_and_apply_esp_stream()
    print("🚀 Starting Smart Waste Monitoring System...")
    print("📍 Local URL: http://localhost:10000")
    print("👤 Login Credentials:")
    print("   Admin: admin / admin123")
    print("   Officer: officer / waste2026")
    print("♻️ Ready for waste detection!")
    print("-" * 50)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=10000,
        debug=True,
        load_dotenv=False,
    )