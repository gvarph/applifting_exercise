from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..logger import get_logger

from ..errors import CustomException

logger = get_logger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except StarletteHTTPException as e:
            logger.error(f"Starlette HTTP Exception: {str(e)}")
            response = JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except CustomException as e:  # Catch any custom exception
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=e.response_code)
        except Exception as e:
            logger.error(f"Unexpected Exception: {str(e)}")
            response = JSONResponse(
                {"detail": "An unexpected error occurred"}, status_code=500
            )
            raise e
        return response
