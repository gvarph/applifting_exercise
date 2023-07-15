class AuthenticationFailedError(Exception):
    """Exception raised for errors in the authentication process"""

    def __init__(self, message="Authentication Failed"):
        self.message = message
        super().__init__(self.message)


class InvalidJwtTokenError(Exception):
    """Exception raised for errors in decoding JWT token"""

    def __init__(self, message="Invalid JWT Token"):
        self.message = message
        super().__init__(self.message)


class ApiRequestError(Exception):
    """Exception raised for errors in the API request for token"""

    def __init__(self, message="API request for token failed"):
        self.message = message
        super().__init__(self.message)


class OffersFetchError(Exception):
    """Exception raised for errors in the API request for fetching offers"""

    def __init__(self, message="API request for fetching offers failed"):
        self.message = message
        super().__init__(self.message)


class ProductRegistrationError(Exception):
    """Exception raised for errors in the product registration process"""

    def __init__(self, message="Product registration failed"):
        self.message = message
        super().__init__(self.message)
