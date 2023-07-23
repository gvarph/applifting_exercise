from fastapi.routing import APIRouter

from ..exceptions.internal import InvalidLogin

from ..logger import get_logger
from ..auth import create_token, fake_users_db, validate_password
from ..pydantic_models import AuthModel


router = APIRouter()

logger = get_logger(__name__)

# This could done better (mainly using an DB instead of a dict), but it's not the focus of this project as the auth was a bonus task.
# It would also be smart to add ad something like a option to register in the application, or something more complex like token refresh.


@router.post("/token")
def login(authData: AuthModel) -> dict[str, str]:
    """
    Authenticate user and generate an access token.

    Parameters:
    - authData (AuthModel): User authentication data containing `username` and `password`.

    Returns:
    - dict[str, str]: A dictionary containing the generated access `token`.

    Raises:
    - InvalidLogin: If the user is not found or the password is invalid.
    """

    if authData.username not in fake_users_db or not validate_password(
        authData.password, fake_users_db[authData.username]
    ):
        raise InvalidLogin(f"User does not exist or the password is invalid")

    token: str = create_token(authData.username)
    logger.debug(f"Token created for user {authData.username}")

    return {"token": token}
