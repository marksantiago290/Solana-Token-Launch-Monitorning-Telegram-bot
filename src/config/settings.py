import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

API_BASE_URL = os.getenv("API_SERVER_URL", "http://localhost:8000")

# Bot configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_USER_IDS = list(map(int, os.getenv("ADMIN_USER_IDS", "").split(",")))

# Blockchain configuration
WEB3_PROVIDER_URI_KEY = os.getenv("WEB3_PROVIDER_URI_KEY")
SOL_PROVIDER_URL=os.getenv("SOL_PROVIDER_URL")
SOLANA_TOKEN_PROGRAM_ID=os.getenv("SOLANA_TOKEN_PROGRAM_ID") 

# Database configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "new_token_sol")
