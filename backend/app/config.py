import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-key")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", Config.FRONTEND_URL if False else "http://localhost:5173").split(',') if x.strip()]
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    DEV_AUTH_ENABLED = os.getenv("DEV_AUTH_ENABLED", "true").lower() == "true"
