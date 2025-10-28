import os
import cv2
import torch
import argparse
from torchvision import transforms
from PIL import Image
from ultralytics import YOLO
from models import CNN_LSTM

# =====================================================
# CONFIGURATION
# =====================================================
MODEL_VIOLENCE_PATH = "cnn_lstm.pth"
MODEL_WEAPON_PATH = "best.pt"
INPUT_DIR = "Input"       # Folder containing input videos
OUTPUT_DIR = "Output"     # Folder to save processed videos

SEQ_LEN = 16
FRAME_RATE = 5
CONF_THRESHOLD = 0.7

# =====================================================
# DEVICE SETUP
# =====================================================
device = "cuda" if torch.cuda.is_available() else "cpu"

# =====================================================
# IMAGE TRANSFORM (must match CNN-LSTM training)
# =====================================================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# =====================================================
# LOAD MODELS
# =====================================================
# 1️⃣ Violence Detection Model
violence_model = CNN_LSTM()
violence_model.load_state_dict(torch.load(MODEL_VIOLENCE_PATH, map_location=device))
violence_model.to(device)
violence_model.eval()

# 2️⃣ Weapon Detection Model
weapon_model = YOLO(MODEL_WEAPON_PATH)

# =====================================================
# FUNCTION: Load Frames for Violence Model
# =====================================================
def load_clip_from_video(video_path, seq_len=16, frame_rate=5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"❌ Could not open video file: {video_path}")

    frames = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_rate == 0:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = transform(img)
            frames.append(img)
        frame_count += 1

    cap.release()

    if len(frames) < seq_len:
        raise ValueError(f"Not enough frames ({len(frames)}), need {seq_len}")

    indices = torch.linspace(0, len(frames) - 1, steps=seq_len).long()
    selected = [frames[i] for i in indices]
    clip = torch.stack(selected).unsqueeze(0).to(device)
    return clip

# =====================================================
# FUNCTION: Predict Violence
# =====================================================
def predict_violence(video_path):
    clip = load_clip_from_video(video_path, SEQ_LEN, FRAME_RATE)
    with torch.no_grad():
        prob = violence_model(clip).item()
    label = "Violence" if prob >= 0.5 else "Non-Violence"
    return label, prob

# =====================================================
# FUNCTION: Process Frame for Weapon Detection
# =====================================================
def process_frame_weapon(frame, model, conf_threshold=0.7):
    results = model.predict(frame, conf=conf_threshold, verbose=False)
    boxes = results[0].boxes
    weapon_boxes = [b for b, cls in zip(boxes.xyxy, boxes.cls) if int(cls) == 0] if boxes else []

    if len(weapon_boxes) > 0:
        label = "Weapon Detected"
        color = (0, 0, 255)
    else:
        label = "No Weapon"
        color = (0, 255, 0)

    for box in weapon_boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    return frame, len(weapon_boxes) > 0, label

# =====================================================
# MAIN PROCESSING FUNCTION
# =====================================================
def process_video(video_path, output_path):
    print(f"\n🎥 Processing: {os.path.basename(video_path)}")

    # Predict violence for the entire video
    try:
        violence_label, violence_prob = predict_violence(video_path)
    except Exception as e:
        print(f"❌ Error processing violence for {video_path}: {e}")
        return

    violence_detected = violence_label == "Violence"

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 20

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    weapon_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, weapon_in_frame, weapon_label = process_frame_weapon(frame, weapon_model, CONF_THRESHOLD)
        if weapon_in_frame:
            weapon_detected = True

        # Check DANGER condition
        danger = violence_detected or weapon_detected
        danger_label = "🚨 DANGER" if danger else "✅ SAFE"
        danger_color = (0, 0, 255) if danger else (0, 255, 0)

        # Overlay text
        text1 = f"{violence_label.upper()} ({violence_prob:.2f})"
        text2 = f"{weapon_label.upper()}"
        cv2.putText(frame, text1, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    (0, 0, 255) if violence_label == "Violence" else (0, 255, 0), 3)
        cv2.putText(frame, text2, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (0, 0, 255) if weapon_in_frame else (0, 255, 0), 2)
        cv2.putText(frame, danger_label, (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 1.3, danger_color, 3)

        out.write(frame)

    cap.release()
    out.release()

    # Final status summary
    if violence_detected or weapon_detected:
        alert_status = "🚨 DANGER DETECTED"
    else:
        alert_status = "✅ SAFE"

    print(f"✅ Saved: {output_path}")
    print(f"🧠 Violence: {violence_label} ({violence_prob:.2f}) | 🔫 Weapon: {'Yes' if weapon_detected else 'No'} | ⚠️ Status: {alert_status}")

# =====================================================
# RUN PIPELINE FOR ALL VIDEOS IN INPUT DIR
# =====================================================
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    videos = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
    if not videos:
        print(f"⚠️ No videos found in '{INPUT_DIR}' folder.")
        exit()

    print(f"📂 Found {len(videos)} video(s) in '{INPUT_DIR}'")

    for video_name in videos:
        input_path = os.path.join(INPUT_DIR, video_name)
        output_path = os.path.join(OUTPUT_DIR, f"output_{video_name}")
        process_video(input_path, output_path)

    print("\n🏁 All videos processed successfully!")
