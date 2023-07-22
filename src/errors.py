from abc import ABC
from fastapi import HTTPException

# I have made a bit of a mess here, but I don't have the time to clean it up right now.
# Main problem is that I use the same http request related exceptions while providing and API and requesting another API.


class CustomException(HTTPException):
    """Base class for custom exceptions"""

    def __init__(self, status_code=500, detail="An unexpected error occurred"):
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationFailedError(CustomException):
    """Exception raised for errors in the authentication process"""

    def __init__(self, detail="Authentication Failed"):
        super().__init__(status_code=401, detail=detail)


class InvalidJwtTokenError(CustomException):
    """Exception raised for errors in decoding JWT token"""

    def __init__(self, detail="Invalid JWT Token"):
        super().__init__(status_code=401, detail=detail)


class ApiRequestError(CustomException):
    """Exception raised for errors in the API request for token"""

    def __init__(self, detail="API request failed"):
        super().__init__(status_code=400, detail=detail)


class OffersFetchError(CustomException):
    """Exception raised for errors in the API request for fetching offers"""

    def __init__(self, detail="Offers fetch failed"):
        super().__init__(status_code=500, detail=detail)


class ProductRegistrationError(CustomException):
    """Exception raised for errors in the product registration process"""

    def __init__(self, detail="Product registration failed"):
        super().__init__(status_code=500, detail=detail)


class EntityNotFound(CustomException):
    """Exception raised for errors caused by missing entities"""

    def __init__(self, detail="Entity not found"):
        super().__init__(status_code=404, detail=detail)


class InvalidCredentialsException(CustomException):
    """Exception raised for errors caused by invalid credentials"""

    def __init__(self, detail="Invalid credentials"):
        super().__init__(status_code=401, detail=detail)


class EnvironmentVariableNotSet(CustomException):
    """Exception raised for errors caused by missing environment variables"""

    def __init__(self, detail="Environment variable not set"):
        super().__init__(status_code=500, detail=detail)


class InvalidLogin(CustomException):
    """Exception raised for errors caused by failed login"""

    def __init__(self, detail="Invalid login") -> None:
        super().__init__(status_code=401, detail=detail)


class InvalidTimeRangeError(CustomException):
    """Exception raised for errors caused by invalid time range"""

    def __init__(self, detail="Start time cannot be greater than end time"):
        super().__init__(status_code=400, detail=detail)


class JWTSignatureExpiredError(CustomException):
    """Exception raised for errors caused by expired JWT token"""

    def __init__(self, detail="JWT Signature expired"):
        super().__init__(status_code=401, detail=detail)


class JWTInvalidTokenError(CustomException):
    """Exception raised for errors caused by invalid JWT token"""

    def __init__(self, detail="Invalid JWT token"):
        super().__init__(status_code=401, detail=detail)
