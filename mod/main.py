# weapon_video_detection.py

import cv2
from ultralytics import YOLO

# =======================
# USER CONFIGURATION
# =======================
MODEL_PATH = 'best.pt'  # path to your YOLOv8 model
INPUT_VIDEO = '3223449-uhd_3840_2160_24fps.mp4'  # path to input video
OUTPUT_VIDEO = 'output_weapon_detection.mp4'  # path to save output
CONF_THRESHOLD = 0.7  # confidence threshold

# =======================
# LOAD YOLOv8 MODEL
# =======================
model = YOLO(MODEL_PATH)

# =======================
# FUNCTION TO PROCESS FRAME
# =======================
def process_frame(frame, model, conf_threshold=0.6):
    results = model.predict(frame, conf=conf_threshold)
    boxes = results[0].boxes

    # Filter boxes for class 0 (weapon)
    weapon_boxes = [b for b, cls in zip(boxes.xyxy, boxes.cls) if int(cls) == 0] if boxes else []

    if len(weapon_boxes) > 0:
        label = "Weapon Detected"
        color = (0, 0, 255)  # Red
    else:
        label = "No Weapon"
        color = (0, 255, 0)  # Green

    # Draw label on frame
    cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)

    # Draw bounding boxes
    for box in weapon_boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    return frame, len(weapon_boxes) > 0

# =======================
# VIDEO PROCESSING
# =======================
cap = cv2.VideoCapture(INPUT_VIDEO)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# VideoWriter to save output
out = cv2.VideoWriter(OUTPUT_VIDEO, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

weapon_detected_in_video = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Process frame
    frame, weapon_in_frame = process_frame(frame, model, CONF_THRESHOLD)
    if weapon_in_frame:
        weapon_detected_in_video = True

    # Write to output
    out.write(frame)

    # Display live (optional)
    cv2.imshow('Weapon Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"✅ Processed video saved at: {OUTPUT_VIDEO}")

# =======================
# FINAL CONCLUSION
# =======================
if weapon_detected_in_video:
    print("⚠️ Final Conclusion: Weapon Detected in Video")
else:
    print("✅ Final Conclusion: No Weapon Detected in Video")