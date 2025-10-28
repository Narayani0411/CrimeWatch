# detection.py
import cv2

def detect_crime(video_path: str, detection_threshold: float = 0.5):
    """
    Dummy crime detection function.
    video_path: path to the uploaded video
    detection_threshold: placeholder, not used here yet
    Returns:
        detected (bool): True if suspicious activity detected
        label (str): label of detected activity
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False, "Video cannot be opened"

    frame_count = 0
    detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % 50 == 0:
            detected = True
            label = "Suspicious activity"
            break

    cap.release()

    if detected:
        return True, label
    else:
        return False, "No suspicious activity"
