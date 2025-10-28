import os
import cv2
import torch
import argparse
from torchvision import transforms
from PIL import Image
from models import CNN_LSTM

# Device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Transforms (must match training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


def load_clip_from_video(video_path, seq_len=16, frame_rate=5):
    """
    Reads frames directly from video file and returns a tensor clip.
    """
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
            # Convert frame (BGR → RGB)
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = transform(img)
            frames.append(img)
        frame_count += 1

    cap.release()

    if len(frames) < seq_len:
        raise ValueError(f"Not enough frames in {video_path} (found {len(frames)}, need {seq_len})")

    # Uniformly sample seq_len frames
    indices = torch.linspace(0, len(frames)-1, steps=seq_len).long()
    selected = [frames[i] for i in indices]

    clip = torch.stack(selected)  # (seq_len, C, H, W)
    clip = clip.unsqueeze(0).to(device)  # add batch dim
    return clip

def predict(video_path, seq_len=16, frame_rate=5):
    """
    Predict violence vs non-violence directly from video.
    """
    clip = load_clip_from_video(video_path, seq_len, frame_rate)

    with torch.no_grad():
        prob = model(clip).item()

    label = "violence" if prob >= 0.5 else "non_violence"
    return label, prob

if __name__ == "__main__":
    INPUT_VIDEO= "Street fighter kick #selfdenfense #streetdefence #mma.mp4"
    OUTPUT_VIDEO = 'output_voilence.mp4'
    # Default video paths

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=INPUT_VIDEO, help="Path to input video (.mp4)")
    parser.add_argument("--seq_len", type=int, default=16, help="Number of frames per clip")
    parser.add_argument("--frame_rate", type=int, default=5, help="Sample every Nth frame")
    args = parser.parse_args()

    # Load trained model
    model = CNN_LSTM()
    model.load_state_dict(torch.load("cnn_lstm.pth", map_location=device))
    model.to(device)
    model.eval()

    # Run prediction
    label, prob = predict(args.input, seq_len=args.seq_len, frame_rate=args.frame_rate)
    print(f"Prediction: {label} (confidence={prob:.4f})")

    # Overlay result on video and save
    cap = cv2.VideoCapture(args.input)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, 20.0,
                          (int(cap.get(3)), int(cap.get(4))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        text = f"{label.upper()} ({prob:.2f})"
        color = (0, 0, 255) if label == "violence" else (0, 255, 0)
        cv2.putText(frame, text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, color, 3, cv2.LINE_AA)
        out.write(frame)

    cap.release()
    out.release()
    print(f"✅ Output video saved to {OUTPUT_VIDEO}")
