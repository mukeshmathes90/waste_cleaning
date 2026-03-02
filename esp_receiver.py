from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ===== YOUR PUBLIC WEBSITE =====
CLOUD_URL = "https://smartwaste.onrender.com/analyze"

# folder to temporarily save images
SAVE_FOLDER = "received_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST'])
def receive_image():
    try:
        # create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"esp_{timestamp}.jpg"
        filepath = os.path.join(SAVE_FOLDER, filename)

        # save image from ESP
        with open(filepath, "wb") as f:
            f.write(request.data)

        print(f"✅ Image received from ESP: {filename}")

        # ===== FORWARD TO CLOUD =====
        with open(filepath, "rb") as img:
            response = requests.post(
                CLOUD_URL,
                files={"file": img}
            )

        print("☁️ Sent to cloud:", response.status_code)

        return "Image received & forwarded", 200

    except Exception as e:
        print("❌ Error:", e)
        return "Failed", 500


if __name__ == "__main__":
    # IMPORTANT: same port ESP already uses
    app.run(host="0.0.0.0", port=80)