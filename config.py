import os
from datetime import timedelta
from dotenv import load_dotenv

# 🔑 THIS IS THE FIX
load_dotenv()

class Config:
    # ================= CORE SECURITY =================
    SECRET_KEY = os.getenv("SECRET_KEY", "smartgatepass_secret")

    # ================= JWT AUTH =================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_smart_gatepass")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # ================= QR SECURITY =================
    QR_SECRET_KEY = os.getenv("QR_SECRET_KEY", "smartgatepass_qr_secret")

    # ================= DATABASE (LOCAL + RENDER) =================
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise RuntimeError("DATABASE_URL not set. Check your .env file")

    # Fix Render postgres:// issue
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ================= ERROR HANDLING =================
    PROPAGATE_EXCEPTIONS = True