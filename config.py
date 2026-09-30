import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "bustrackerai-dev-secret-key-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "bustrackerai-jwt-secret-change-me")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/bustrackerai")
    DB_NAME = os.getenv("DB_NAME", "bustrackerai")
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "24"))
    CANCELLATION_HOURS_BEFORE = int(os.getenv("CANCELLATION_HOURS_BEFORE", "1"))
    GST_PERCENT = float(os.getenv("GST_PERCENT", "5.0"))
