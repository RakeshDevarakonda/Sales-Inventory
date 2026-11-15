import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Security / JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# Business Rules
APPROVAL_THRESHOLD_AMOUNT = Decimal(os.getenv("APPROVAL_THRESHOLD_AMOUNT"))

# Email Configuration
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT")) if os.getenv("MAIL_PORT") else None
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")

# CORS Origins
raw_cors = os.getenv("CORS_ORIGINS")
CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()] if raw_cors else []
