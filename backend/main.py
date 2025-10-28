# server.py
import os
import io
import base64
import datetime
from collections import defaultdict, deque
from typing import List

import uvicorn
import torch
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

from ultralytics import YOLO
from pymongo import MongoClient

# --- import your CNN_LSTM model ---
from models import CNN_LSTM

# =====================================================
# CONFIG
# =====================================================
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

MODEL_WEAPON_PATH = "best.pt"
MODEL_VIOLENCE_PATH = "cnn_lstm.pth"
TEMP_DIR = "temp_snapshots"
os.makedirs(TEMP_DIR, exist_ok=True)

ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "60"))  # seconds
SEQ_LEN = int(os.getenv("SEQ_LEN", "16"))

# =====================================================
# DEVICE + TRANSFORMS
# =====================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# =====================================================
# MODEL LOADING
# =====================================================
print("🔁 Loading models...")
weapon_model = YOLO(MODEL_WEAPON_PATH)

violence_model = CNN_LSTM()
violence_state = torch.load(MODEL_VIOLENCE_PATH, map_location=device)

# Clean up state dict
if isinstance(violence_state, dict) and any(k.startswith("module") or k.endswith("state_dict") for k in violence_state.keys()):
    v_state = violence_state.get("state_dict", violence_state)
else:
    v_state = violence_state

clean_state = {k.replace("module.", ""): v for k, v in v_state.items()}
violence_model.load_state_dict(clean_state)
violence_model.to(device)
violence_model.eval()
print("✅ Models loaded successfully.")

# =====================================================
# DATABASE & FASTAPI
# =====================================================
client = MongoClient(MONGODB_URI)
db = client["crimewatch"]
alerts_collection = db["alerts"]

app = FastAPI(title="CrimeWatch AI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# GLOBAL BUFFERS
# =====================================================
frame_buffers = defaultdict(lambda: deque(maxlen=SEQ_LEN))
last_alert_time = None

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def pil_from_bgr(bgr):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

def predict_violence_from_buffer(buffer_deque):
    try:
        tensors = [transform(pil_from_bgr(f)) for f in list(buffer_deque)]
        clip = torch.stack(tensors).unsqueeze(0).to(device)
        with torch.no_grad():
            out = violence_model(clip)
            prob = float(out.squeeze().cpu().item())
        label = "Violence" if prob >= 0.5 else "Non-Violence"
        return label, prob
    except Exception as e:
        print("Violence prediction error:", e)
        return "Error", 0.0

def detect_weapons_in_frame(frame, conf_threshold=0.5):
    try:
        results = weapon_model.predict(frame, conf=conf_threshold, verbose=False)
        boxes = results[0].boxes
        weapon_boxes = []
        if boxes is not None and len(boxes) > 0:
            for box, cls in zip(boxes.xyxy, boxes.cls):
                if int(cls) == 0:  # assuming class 0 is weapon
                    x1, y1, x2, y2 = map(int, box.tolist())
                    weapon_boxes.append([x1, y1, x2, y2])
        return weapon_boxes
    except Exception as e:
        print("YOLO error:", e)
        return []

def send_email_alert(location: str, dt: str, file_path: str, danger_label: str):
    if not SENDGRID_API_KEY or not ALERT_EMAIL or not SENDER_EMAIL:
        print("⚠️ SendGrid or email config missing.")
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
        subject=f"CrimeWatch Alert: {danger_label}",
        html_content=f"<strong>{danger_label}</strong> detected at {location} on {dt}.",
    )
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("📧 Email sent:", response.status_code)
        return {"status": "sent", "code": response.status_code}
    except Exception as e:
        print("Email error:", e)
        return {"status": "error", "message": str(e)}

def send_email_if_cooldown(location: str, dt: str, file_path: str, danger_label: str):
    global last_alert_time
    now = datetime.datetime.now()
    if last_alert_time and (now - last_alert_time).total_seconds() < ALERT_COOLDOWN:
        print("Skipping email due to cooldown")
        return {"status": "skipped_cooldown"}
    last_alert_time = now
    return send_email_alert(location, dt, file_path, danger_label)

# =====================================================
# API ENDPOINTS
# =====================================================
@app.post("/upload-frame/")
async def upload_frame(frame: UploadFile = File(...), camera_id: str = Form("camera_01")):
    """
    Upload a single frame, run detection, log alert.
    """
    content = await frame.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "Invalid image data."}

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    location = camera_id

    # 1️⃣ Weapon detection
    weapon_boxes = detect_weapons_in_frame(img)
    weapon_detected = len(weapon_boxes) > 0

    # 2️⃣ Violence detection
    buf = frame_buffers[camera_id]
    buf.append(img.copy())
    violence_label, violence_prob = ("NotEnoughFrames", 0.0)
    if len(buf) == SEQ_LEN:
        violence_label, violence_prob = predict_violence_from_buffer(buf)

    violence_detected = violence_label == "Violence"
    danger = weapon_detected or violence_detected
    danger_label = "Violence/Weapon" if danger else "Safe"

    # 3️⃣ Save snapshot (local only)
    snapshot_path = None
    email_status = {"status": "none"}
    if danger:
        basename = f"alert_{camera_id}_{int(datetime.datetime.now().timestamp())}.png"
        snapshot_path = os.path.join(TEMP_DIR, basename)
        cv2.imwrite(snapshot_path, img)
        email_status = send_email_if_cooldown(location, dt, snapshot_path, danger_label)

    # 4️⃣ Log to MongoDB
    alert_doc = {
        "timestamp": dt,
        "camera_id": camera_id,
        "danger_status": danger_label,
        "violence_label": violence_label,
        "violence_prob": violence_prob,
        "weapon_detected": weapon_detected,
        "snapshot_path": snapshot_path,
        "email_status": email_status,
    }
    alerts_collection.insert_one(alert_doc)

    return {"message": "Frame processed", "danger": danger, "timestamp": dt, "status": danger_label}

@app.get("/alerts/")
def get_alerts(limit: int = 20):
    """
    Return only timestamps and essential info for alert page.
    """
    docs = list(alerts_collection.find({}, {"timestamp": 1, "camera_id": 1, "danger_status": 1, "_id": 0})
                .sort("timestamp", -1)
                .limit(limit))
    return {"alerts": docs}

@app.get("/snapshot/{filename}")
def get_snapshot(filename: str):
    path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(path):
        return {"error": "File not found."}
    return FileResponse(path, media_type="image/png")

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    print("🚀 Starting CrimeWatch AI backend at http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)