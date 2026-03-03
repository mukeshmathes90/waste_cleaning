from flask import Flask, request
import requests
import os
from datetime import datetime
import socket

app = Flask(__name__)

# Your main app analyze endpoint
MAIN_APP_URL = "http://127.0.0.1:10000/analyze"

TEMP_FOLDER = "bridge_temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def receive_from_esp():
    try:
        if not request.data:
            return "No image received", 400

        # Save temporary image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"esp_{timestamp}.jpg"
        filepath = os.path.join(TEMP_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(request.data)

        print(f"📷 Image received from ESP: {filename}")

        # Forward as multipart/form-data
        with open(filepath, "rb") as img:
            files = {
                "image": (filename, img, "image/jpeg")
            }

            response = requests.post(MAIN_APP_URL, files=files)

        print("➡ Forwarded to Main App:", response.status_code)

        return "Forwarded successfully", 200

    except Exception as e:
        print("❌ Bridge Error:", e)
        return "Bridge failed", 500


if __name__ == "__main__":
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("🚀 ESP Bridge Started")
    print(f"📡 ESP must send to: http://{local_ip}/upload")
    print("--------------------------------------------------")

    app.run(host="0.0.0.0", port=80)