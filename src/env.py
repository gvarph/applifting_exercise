import os
from dotenv import load_dotenv

load_dotenv(".env")


DATABASE_URL = os.getenv("DATABASE_URL")

TOKEN_SECRET = os.getenv("TOKEN_SECRET")

API_URL = os.getenv("API_URL")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
