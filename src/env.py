import os
from dotenv import load_dotenv

from .errors import EnvironmentVariableNotSet

load_dotenv(".env")

# if we are in a test environment, we should be getting the values from pytest.ini


def get_required_env_variable(var_name):
    var = os.getenv(var_name)
    if not var:
        raise EnvironmentVariableNotSet(f"{var_name} is not set")
    return var


# not not is a trick to convert any truthy value to True and any falsy value to False
# This ensures that we can use the the values are booleans
CI = not not os.getenv("CI", False)
TEST_ENV = CI or not not os.getenv("TEST_ENV", False)


TOKEN_SECRET = get_required_env_variable("TOKEN_SECRET")
JWT_SECRET = get_required_env_variable("JWT_SECRET")
DATABASE_URL = get_required_env_variable("DATABASE_URL")

API_URL: str = os.getenv("API_URL", "https://python.exercise.applifting.cz/api/v1")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_TOKEN_EXPIRE_MINUTES", 30))


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

PERIODIC_FETCH_INTERVAL = int(os.getenv("PERIODIC_FETCH_INTERVAL", 60))
