import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Security / JWT
SECRET_KEY = os.getenv("SECRET_KEY", "sales_inventory_insecure_default_secret_key_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))       # 30 mins
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))           # 7 days

# Business Rules
APPROVAL_THRESHOLD_AMOUNT = Decimal(os.getenv("APPROVAL_THRESHOLD_AMOUNT", "1000.00"))

# Email Configuration
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.mailtrap.io")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "noreply@salesinventory.com")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL", "manager@salesinventory.com")
