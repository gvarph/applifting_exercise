# Exceptions related to your API
from .base import CustomException


class InternalApiException(CustomException):
    """Base class for internal API exceptions."""

    pass


class AuthenticationFailedError(InternalApiException):
    """Exception raised for errors in the authentication process."""

    def __init__(self, detail="Authentication Failed"):
        super().__init__(status_code=401, detail=detail)


class InvalidJwtTokenError(InternalApiException):
    """Exception raised for errors in decoding JWT token."""

    def __init__(self, detail="Invalid JWT Token"):
        super().__init__(status_code=401, detail=detail)


class EntityNotFound(InternalApiException):
    """Exception raised for errors caused by missing entities."""

    def __init__(self, detail="Entity not found"):
        super().__init__(status_code=404, detail=detail)


class InvalidCredentialsException(InternalApiException):
    """Exception raised for errors caused by invalid credentials."""

    def __init__(self, detail="Invalid credentials"):
        super().__init__(status_code=401, detail=detail)


class InvalidLogin(InternalApiException):
    """Exception raised for errors caused by failed login."""

    def __init__(self, detail="Invalid login"):
        super().__init__(status_code=401, detail=detail)


class InvalidTimeRangeError(InternalApiException):
    """Exception raised for errors caused by invalid time range."""

    def __init__(self, detail="Start time cannot be greater than end time"):
        super().__init__(status_code=400, detail=detail)


class JWTSignatureExpiredError(InternalApiException):
    """Exception raised for errors caused by expired JWT token."""

    def __init__(self, detail="JWT Signature expired"):
        super().__init__(status_code=401, detail=detail)


class JWTInvalidTokenError(InternalApiException):
    """Exception raised for errors caused by invalid JWT token."""

    def __init__(self, detail="Invalid JWT token"):
        super().__init__(status_code=401, detail=detail)


class EnvironmentVariableNotSet(InternalApiException):
    """Exception raised for errors caused by missing environment variables."""

    def __init__(self, detail="Environment variable not set"):
        super().__init__(status_code=500, detail=detail)


class InvalidProductData(InternalApiException):
    """Exception raised for errors caused by invalid product data."""

    def __init__(self, detail="Invalid product data"):
        super().__init__(status_code=400, detail=detail)
