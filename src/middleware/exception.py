from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..logger import get_logger

from ..exceptions.base import CustomException

logger = get_logger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except CustomException as e:
            logger.error(f"Custom Exception: {str(e)}")
            response = JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except StarletteHTTPException as e:
            logger.error(f"Starlette HTTP Exception: {str(e)}")
            response = JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except Exception as e:
            logger.error(f"Unexpected Exception: {str(e)}")
            response = JSONResponse(
                {"detail": "An unexpected error occurred"}, status_code=500
            )
        return response
