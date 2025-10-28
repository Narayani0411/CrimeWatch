import os
import io
import base64
import datetime
import shutil
from typing import List

import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

import numpy as np
import cv2
from ultralytics import YOLO

# MongoDB
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

# --- Config / env ---
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MODEL_WEAPON_PATH = "best.pt"

TEMP_DIR = "temp_snapshots"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- DB setup ---
client = MongoClient(MONGODB_URI)
db = client["crimewatch"]
alerts_collection = db["alerts"]

# --- YOLO weapon model ---
weapon_model = YOLO(MODEL_WEAPON_PATH)

# --- Cooldown ---
last_alert_time = None
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "60"))  # seconds

app = FastAPI()
# allow your frontend origin(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4200"],  # adjust for your front-end
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def send_email_alert(location: str, dt: str, file_path: str):
    if not SENDGRID_API_KEY or not ALERT_EMAIL or not SENDER_EMAIL:
        print("SendGrid or email config missing, skipping email.")
        return {"status": "disabled"}

    with open(file_path, "rb") as f:
        encoded_file = base64.b64encode(f.read()).decode()

    attachment = Attachment(
        file_content=FileContent(encoded_file),
        file_type=FileType("image/png"),
        file_name=FileName(os.path.basename(file_path)),
        disposition=Disposition("attachment"),
    )

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=ALERT_EMAIL,
        subject="CrimeWatch Alert: Suspicious Frame Detected",
        html_content=f"Suspicious activity detected at {location} on {dt}",
    )
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("Email sent:", response.status_code)
        return {"status": "sent", "code": response.status_code}
    except Exception as e:
        print("Error sending email:", e)
        return {"status": "error", "message": str(e)}


def send_email_if_cooldown(location: str, dt: str, file_path: str):
    global last_alert_time
    now = datetime.datetime.now()
    if last_alert_time and (now - last_alert_time).total_seconds() < ALERT_COOLDOWN:
        print("Skipping email due to cooldown")
        return {"status": "skipped_cooldown"}
    last_alert_time = now
    return send_email_alert(location, dt, file_path)


@app.post("/upload-frame/")
async def upload_frame(frame: UploadFile = File(...)):
    """
    Receives a single image frame (jpeg/png) and performs weapon detection (YOLO).
    If weapon detected saves snapshot, stores alert to MongoDB and triggers email with cooldown.
    """
    content = await frame.read()
    # decode image bytes to cv2 image
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "Could not decode image"}

    # Run YOLO prediction on the image
    try:
        results = weapon_model.predict(img, conf=0.4, verbose=False)  # adjust conf
        res = results[0]
        boxes = res.boxes
        # check classes: assume class 0 is 'weapon' in your training - adjust if different
        weapon_boxes = []
        if boxes is not None and len(boxes) > 0:
            for box, cls in zip(boxes.xyxy, boxes.cls):
                if int(cls) == 0:  # adjust class index if necessary
                    x1, y1, x2, y2 = map(int, box.tolist())
                    weapon_boxes.append([x1, y1, x2, y2])
    except Exception as e:
        print("YOLO error:", e)
        weapon_boxes = []

    weapon_detected = len(weapon_boxes) > 0
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    location = "Camera 01"  # could accept location param in request if you want

    snapshot_path = None
    email_status = {"status": "none"}
    if weapon_detected:
        # save snapshot to disk (PNG)
        basename = f"snapshot_{int(datetime.datetime.now().timestamp())}.png"
        snapshot_path = os.path.join(TEMP_DIR, basename)
        # write image as PNG
        cv2.imwrite(snapshot_path, img)

        # send email if not in cooldown
        email_status = send_email_if_cooldown(location=location, dt=dt, file_path=snapshot_path)

    # store in MongoDB
    alert_doc = {
        "timestamp": dt,
        "location": location,
        "details": "Weapon detected" if weapon_detected else "No weapon",
        "weapon_boxes": weapon_boxes,
        "snapshot_path": snapshot_path,
        "email_status": email_status,
    }
    insert_result = alerts_collection.insert_one(alert_doc)
    alert_doc["_id"] = str(insert_result.inserted_id)

    # create snapshot URL if you plan to serve snapshots via static files (optional)
    # For now, we can return path and the frontend can request /snapshot/{filename} if endpoint exists.
    # Return alert object to frontend
    return {"alert": alert_doc, "weapon_detected": weapon_detected}


@app.get("/alerts/")
def get_alerts(limit: int = 20):
    docs = list(alerts_collection.find().sort("timestamp", -1).limit(limit))
    # convert ObjectId to str
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"alerts": docs}


# Optional endpoint to serve snapshot images (if you want to show them in frontend).
# Make sure static folder is served or use Nginx or similar for production.
@app.get("/snapshot/{filename}")
def get_snapshot(filename: str):
    path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(path):
        return {"error": "Not found"}
    return FileResponse(path, media_type="image/png")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
