import os
from dotenv import load_dotenv

load_dotenv(".env")


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set")

TOKEN_SECRET = os.getenv("TOKEN_SECRET")

if not TOKEN_SECRET:
    raise Exception("TOKEN_SECRET is not set")

API_URL = os.getenv("API_URL")

if not API_URL:
    raise Exception("API_URL is not set")


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

PERIODIC_FETCH_INTERVAL = int(os.getenv("PERIODIC_FETCH_INTERVAL", 60))
