import os
from datetime import timedelta

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "smart_secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret")
    QR_SECRET_KEY = os.getenv("QR_SECRET_KEY", "qr_secret")

    db_url = os.getenv("DATABASE_URL")

    # If running on Render (DATABASE_URL exists)
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
    else:
        # If running locally
        db_url = "sqlite:///local.db"

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)