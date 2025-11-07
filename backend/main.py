# backend/main.py

import os
import datetime
import torch
import numpy as np
import cv2
from collections import defaultdict, deque
from PIL import Image
from torchvision import transforms
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from pymongo import MongoClient
from dotenv import load_dotenv
from ultralytics import YOLO

from .models import CNN_LSTM

# =====================================================
# CONFIG
# =====================================================
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

MODEL_WEAPON_PATH = "backend\\best.pt"
MODEL_VIOLENCE_PATH = "backend\\cnn_lstm.pth"
TEMP_DIR = "backend\\temp_snapshots"
os.makedirs(TEMP_DIR, exist_ok=True)

SEQ_LEN = int(os.getenv("SEQ_LEN", "16"))

# =====================================================
# DATABASE
# =====================================================
client = MongoClient(MONGODB_URI)
db = client["crimewatch"]
alerts_collection = db["alerts"]

# =====================================================
# MODELS
# =====================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

print("🔁 Loading models...")
weapon_model = YOLO(MODEL_WEAPON_PATH)

violence_model = CNN_LSTM()
violence_state = torch.load(MODEL_VIOLENCE_PATH, map_location=device)
clean_state = {k.replace("module.", ""): v for k, v in violence_state.items()}
violence_model.load_state_dict(clean_state)
violence_model.to(device)
violence_model.eval()
print("✅ Models loaded successfully.")

# =====================================================
# HELPERS
# =====================================================
frame_buffers = defaultdict(lambda: deque(maxlen=SEQ_LEN))

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
                if int(cls) == 0:
                    x1, y1, x2, y2 = map(int, box.tolist())
                    weapon_boxes.append([x1, y1, x2, y2])
        return weapon_boxes
    except Exception as e:
        print("YOLO error:", e)
        return []

def send_email_alert(location: str, dt: str, file_path: str, danger_label: str):
    if not SENDGRID_API_KEY or not ALERT_EMAIL or not SENDER_EMAIL:
        print("⚠️ SendGrid config missing.")
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

# =====================================================
# ENDPOINT FUNCTIONS
# =====================================================
async def upload_frame(frame: UploadFile = File(...), camera_id: str = Form("camera_01")):
    """Upload a single frame for analysis"""
    content = await frame.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "Invalid image data."}

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    location = camera_id

    weapon_boxes = detect_weapons_in_frame(img)
    weapon_detected = len(weapon_boxes) > 0

    buf = frame_buffers[camera_id]
    buf.append(img.copy())
    violence_label, violence_prob = ("NotEnoughFrames", 0.0)
    if len(buf) == SEQ_LEN:
        violence_label, violence_prob = predict_violence_from_buffer(buf)

    danger = weapon_detected or violence_label == "Violence"
    danger_label = "Violence/Weapon" if danger else "Safe"

    snapshot_path = None
    email_status = {"status": "none"}
    if danger:
        basename = f"alert_{camera_id}_{int(datetime.datetime.now().timestamp())}.png"
        snapshot_path = os.path.join(TEMP_DIR, basename)
        cv2.imwrite(snapshot_path, img)
        email_status = send_email_alert(location, dt, snapshot_path, danger_label)

    alerts_collection.insert_one({
        "timestamp": dt,
        "camera_id": camera_id,
        "danger_status": danger_label,
        "violence_label": violence_label,
        "violence_prob": violence_prob,
        "weapon_detected": weapon_detected,
        "snapshot_path": snapshot_path,
        "email_status": email_status,
    })

    return {"message": "Frame processed", "status": danger_label}

def get_alerts(limit: int = 20):
    docs = list(
        alerts_collection.find({}, {"timestamp": 1, "camera_id": 1, "danger_status": 1, "_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return {"alerts": docs}

def get_snapshot(filename: str):
    path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(path):
        return {"error": "File not found."}
    return FileResponse(path, media_type="image/png")
