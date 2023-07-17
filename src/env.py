import os
from dotenv import load_dotenv

from .errors import EnvironmentVariableNotSet

load_dotenv(".env")


CI = os.getenv("CI", False)

TEST_ENV = CI or os.getenv("TEST_ENV", False)

_DATABASE_URL = os.getenv("DATABASE_URL")
_TOKEN_SECRET = os.getenv("TOKEN_SECRET")

_JWT_SECRET = os.getenv("JWT_SECRET")

if not _TOKEN_SECRET:
    raise EnvironmentVariableNotSet("TOKEN_SECRET is not set")
TOKEN_SECRET = _TOKEN_SECRET

if not _JWT_SECRET:
    raise EnvironmentVariableNotSet("JWT_SECRET is not set")
JWT_SECRET = _JWT_SECRET

if not _DATABASE_URL:
    raise EnvironmentVariableNotSet("DATABASE_URL is not set")
DATABASE_URL = _DATABASE_URL

# if we are in a test environment, we should be getting the values from pytest.ini

API_URL: str = os.getenv("API_URL", "https://python.exercise.applifting.cz/api/v1")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_TOKEN_EXPIRE_MINUTES", 30))


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

PERIODIC_FETCH_INTERVAL = int(os.getenv("PERIODIC_FETCH_INTERVAL", 60))
