# Exceptions related to external API
from .base import CustomException


class ExternalApiException(CustomException):
    """Base class for external API exceptions."""

    pass


class ApiRequestError(ExternalApiException):
    """Exception raised for errors in the API request for token."""

    def __init__(self, detail="API request failed"):
        super().__init__(status_code=400, detail=detail)


class OffersFetchError(ExternalApiException):
    """Exception raised for errors in the API request for fetching offers."""

    def __init__(self, detail="Offers fetch failed"):
        super().__init__(status_code=500, detail=detail)


class ProductRegistrationError(ExternalApiException):
    """Exception raised for errors in the product registration process."""

    def __init__(self, detail="Product registration failed"):
        super().__init__(status_code=500, detail=detail)


class AuthenticationFailedError(ExternalApiException):
    """Exception raised for errors in the authentication process for a remote API."""

    def __init__(self, detail="Authentication failed"):
        super().__init__(status_code=500, detail=detail)


class InvalidJwtTokenError(ExternalApiException):
    """Exception raised for errors in decoding JWT token."""

    def __init__(self, detail="Invalid JWT token"):
        super().__init__(status_code=500, detail=detail)


class ApiRequestError(ExternalApiException):
    """Exception raised for errors in the API request."""

    def __init__(self, detail="API request failed"):
        super().__init__(status_code=400, detail=detail)
