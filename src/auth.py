from datetime import datetime, timedelta
from fastapi.params import Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
import jwt
from passlib.hash import sha256_crypt

from src.errors import JWTInvalidTokenError, JWTSignatureExpiredError

from .schemas import TokenModel
from .env import JWT_SECRET, ALGORITHM, JWT_TOKEN_EXPIRE_MINUTES
from .logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


def hash_password(password: str) -> str:
    return sha256_crypt.hash(password)


fake_users_db = {
    "johndoe": hash_password("JonhDoe123"),
    "alice": hash_password("Alice123"),
    "bob": hash_password("Bob123"),
    "string": hash_password("string"),
}


def validate_password(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)


def create_token(username: str) -> str:
    to_encode = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return token


def parse_token(token: str) -> TokenModel:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return TokenModel(username=username)
    except jwt.ExpiredSignatureError as e:
        raise JWTSignatureExpiredError()
    except jwt.DecodeError as e:
        raise JWTInvalidTokenError()


def auth_wrapper(auth: HTTPAuthorizationCredentials = Security(security)):
    return parse_token(auth.credentials)
