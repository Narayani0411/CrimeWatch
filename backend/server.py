# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth_router import router as auth_router
from backend.main import upload_frame, get_alerts, get_snapshot

# =====================================================
# APP INITIALIZATION
# =====================================================
app = FastAPI(title="CrimeWatch AI Server")

# =====================================================
# CORS SETUP (MUST be added BEFORE routers)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROUTES
# =====================================================
app.include_router(auth_router)          # Authentication (Signup, Signin, Verify)
app.post("/upload-frame/")(upload_frame) # Frame Upload API
app.get("/alerts/")(get_alerts)          # Alerts fetch API
app.get("/snapshot/{filename}")(get_snapshot)  # Snapshot API

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting backend with proper CORS")
    uvicorn.run(app, host="0.0.0.0", port=8000)
