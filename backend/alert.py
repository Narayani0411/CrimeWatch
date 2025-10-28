import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import datetime

# --- Load Environment Variables ---
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# --- Alert Cooldown Setup ---
last_alert_time = None
ALERT_COOLDOWN = 60  # seconds

# --- SendGrid Email Function with Attachment ---
def send_email_alert(location: str, dt: str, file_path: str):
    with open(file_path, "rb") as f:
        file_data = f.read()
    encoded_file = base64.b64encode(file_data).decode()

    attachment = Attachment()
    attachment.file_content = FileContent(encoded_file)
    attachment.file_type = FileType("image/png")
    attachment.file_name = FileName(os.path.basename(file_path))
    attachment.disposition = Disposition("attachment")

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=ALERT_EMAIL,
        subject="Crime Alert!",
        html_content=f"Suspicious activity detected at {location} on {dt}",
    )
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent, status code: {response.status_code}")
        return {"status": "sent", "code": response.status_code}
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"status": "error", "message": str(e)}

# --- Cooldown Wrapper ---
def send_email_if_cooldown(location: str, dt: str, file_path: str):
    global last_alert_time
    now = datetime.datetime.now()
    if last_alert_time and (now - last_alert_time).total_seconds() < ALERT_COOLDOWN:
        print("Alert skipped due to cooldown")
        return {"status": "skipped_cooldown"}
    last_alert_time = now
    return send_email_alert(location, dt, file_path)

# --- Placeholder Detection ---
def placeholder_detection_logic(video_path: str) -> dict:
    print(f"--- MOCK ANALYSIS: Analyzing video at {video_path} ---")
    detection_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "suspicious": True,
        "location": "Camera 01 (Mock Location)",
        "datetime": detection_time,
        "details": "Simulated weapon detection"
    }
    print(f"--- MOCK ANALYSIS: Finished. Result: {result['details']} ---")
    return result

# --- FastAPI App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_VIDEO_DIR = "temp_videos"
os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

# --- Upload Endpoint ---
@app.post("/upload-video/")
async def analyze_video(video: UploadFile = File(...)):
    temp_file_path = os.path.join(TEMP_VIDEO_DIR, video.filename)
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    finally:
        video.file.close()

    analysis_result = placeholder_detection_logic(temp_file_path)

    if analysis_result.get("suspicious"):
        print("Suspicious activity detected! Sending email alert...")
        email_status = send_email_if_cooldown(
            location=analysis_result.get("location"),
            dt=analysis_result.get("datetime"),
            file_path=temp_file_path
        )
        return {
            "status": "Alert Sent",
            "details": analysis_result,
            "email_status": email_status
        }
    else:
        return {
            "status": "Analysis Complete",
            "details": "No suspicious activity detected."
        }

@app.get("/")
def read_root():
    return {"message": "CrimeWatch API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
