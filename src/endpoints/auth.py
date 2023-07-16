from fastapi import HTTPException
from fastapi.routing import APIRouter

from ..util import get_logger
from ..auth import create_token, fake_users_db, hash_password, validate_password
from ..schemas import AuthModel


router = APIRouter()

logger = get_logger(__name__)


@router.post("/token")
def login(authData: AuthModel) -> dict[str, str]:
    if authData.username not in fake_users_db:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not validate_password(authData.password, fake_users_db[authData.username]):
        logger.debug(
            f"Invalid password for user {authData.username}\n{authData.password=}->{hash_password(authData.password)=}\n{fake_users_db[authData.username]=}"
        )

        raise HTTPException(status_code=401, detail="Invalid password")

    token: str = create_token(authData.username)
    logger.debug(f"Token created for user {authData.username}\n{token=}")

    return {"token": token}
