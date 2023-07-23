from abc import ABC
from fastapi import HTTPException


class CustomException(HTTPException):
    """Base class for custom exceptions"""

    def __init__(self, status_code=500, detail="An unexpected error occurred"):
        super().__init__(status_code=status_code, detail=detail)
