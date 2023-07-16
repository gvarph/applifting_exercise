import os
from dotenv import load_dotenv

load_dotenv(".env")


DATABASE_URL_UNCHECKED = os.getenv("DATABASE_URL")
if not DATABASE_URL_UNCHECKED:
    raise Exception("DATABASE_URL is not set")
DATABASE_URL = DATABASE_URL_UNCHECKED


TOKEN_SECRET_UNCHECKED = os.getenv("TOKEN_SECRET")
if not TOKEN_SECRET_UNCHECKED:
    raise Exception("TOKEN_SECRET is not set")
TOKEN_SECRET = TOKEN_SECRET_UNCHECKED


API_URL = os.getenv("API_URL", "https://python.exercise.applifting.cz/api/v1")


JWT_SECRET_UNCHEKCED = os.getenv("JWT_SECRET")
if not JWT_SECRET_UNCHEKCED:
    raise Exception("JWT_SECRET is not set")
JWT_SECRET = JWT_SECRET_UNCHEKCED
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_TOKEN_EXPIRE_MINUTES", 30))


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

PERIODIC_FETCH_INTERVAL = int(os.getenv("PERIODIC_FETCH_INTERVAL", 60))
