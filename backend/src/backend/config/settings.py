import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Security / JWT
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_in_production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Business Rules (Fallback to 1000.00 if not set in env; can also be managed dynamically in DB)
APPROVAL_THRESHOLD_AMOUNT = Decimal(os.getenv("APPROVAL_THRESHOLD_AMOUNT", "1000.00"))

# Frontend Application URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Email Configuration
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT")) if os.getenv("MAIL_PORT") else None
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")

# CORS Origins
raw_cors = os.getenv("CORS_ORIGINS")
CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()] if raw_cors else []
