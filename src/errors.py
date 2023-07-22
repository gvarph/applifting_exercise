from abc import ABC

# I have made a bit of a mess here, but I don't have the time to clean it up right now.
# Main problem is that I use the same http request related exceptions while providing and API and requesting another API.


class CustomException(Exception, ABC):
    """Base class for custom exceptions"""

    response_code = 500
    user_message = "An unexpected error occurred"

    def __init__(self, message="An unexpected error occurred"):
        self.message = message
        super().__init__(self.message)


class AuthenticationFailedError(CustomException):
    """Exception raised for errors in the authentication process"""

    response_code = 401

    def __init__(self, message="Authentication Failed"):
        super().__init__(message)


class InvalidJwtTokenError(CustomException):
    """Exception raised for errors in decoding JWT token"""

    response_code = 401

    def __init__(self, message="Invalid JWT Token"):
        super().__init__(message)


class ApiRequestError(CustomException):
    """Exception raised for errors in the API request for token"""

    response_code = 400

    def __init__(self, message="API request for token failed"):
        super().__init__(message)


class OffersFetchError(CustomException):
    """Exception raised for errors in the API request for fetching offers"""

    response_code = 500

    def __init__(self, message="API request for fetching offers failed"):
        super().__init__(message)


class ProductRegistrationError(CustomException):
    """Exception raised for errors in the product registration process"""

    response_code = 500

    def __init__(self, message="Product registration failed"):
        super().__init__(message)


class EntityNotFound(CustomException):
    """Exception raised for errors caused by missing entities"""

    response_code = 404

    def __init__(self, message="Entity not found"):
        super().__init__(message)


class InvalidCredentialsException(CustomException):
    """Exception raised for errors caused by invalid credentials"""

    response_code = 401

    def __init__(self, message="Invalid credentials"):
        super().__init__(message)


class EnvironmentVariableNotSet(CustomException):
    """Exception raised for errors caused by missing environment variables"""

    response_code = 500

    def __init__(self, message="Environment variable not set"):
        super().__init__(message)


class InvalidLogin(CustomException):
    """Exception raised for errors caused by failed login"""

    response_code = 401

    def __init__(self, message="Login failed"):
        super().__init__(message)


class InvalidTimeRangeError(CustomException):
    """Exception raised for errors caused by invalid time range"""

    response_code = 400

    def __init__(self, message="Invalid time range"):
        super().__init__(message)
