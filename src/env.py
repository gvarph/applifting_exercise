import os
from dotenv import load_dotenv

from .errors import EnvironmentVariableNotSet

load_dotenv(".env")


CI = os.getenv("CI", False)

TEST_ENV = CI or os.getenv("TEST_ENV", False)

DATABASE_URL_UNCHECKED = os.getenv("DATABASE_URL")
if not DATABASE_URL_UNCHECKED:
    raise Exception("DATABASE_URL is not set")
DATABASE_URL = DATABASE_URL_UNCHECKED


TOKEN_SECRET_UNCHECKED: str | None = os.getenv("TOKEN_SECRET")


API_URL = os.getenv("API_URL", "https://python.exercise.applifting.cz/api/v1")


JWT_SECRET_UNCHEKCED = os.getenv("JWT_SECRET")

if CI:
    TOKEN_SECRET = "sample_token_secret"
    DATABASE_URL = None
else:
    if not TOKEN_SECRET_UNCHECKED:
        raise EnvironmentVariableNotSet("TOKEN_SECRET is not set")

    if not JWT_SECRET_UNCHEKCED:
        raise EnvironmentVariableNotSet("JWT_SECRET is not set")

    TOKEN_SECRET = TOKEN_SECRET_UNCHECKED

    JWT_SECRET = JWT_SECRET_UNCHEKCED


ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_TOKEN_EXPIRE_MINUTES", 30))


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

PERIODIC_FETCH_INTERVAL = int(os.getenv("PERIODIC_FETCH_INTERVAL", 60))
