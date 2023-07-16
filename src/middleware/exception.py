from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..logger import get_logger

from ..errors import (
    AuthenticationFailedError,
    InvalidJwtTokenError,
    ApiRequestError,
    OffersFetchError,
    ProductRegistrationError,
    EntityNotFound,
    InvalidCredentialsException,
)

logger = get_logger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except StarletteHTTPException as e:
            logger.error(f"Starlette HTTP Exception: {str(e)}")
            response = JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except AuthenticationFailedError as e:
            logger.error(f"Authentication Failed Error: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=401)
        except InvalidJwtTokenError as e:
            logger.error(f"Invalid JWT Token Error: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=401)
        except ApiRequestError as e:
            logger.error(f"API Request Error: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=502)
        except OffersFetchError as e:
            logger.error(f"Offers Fetch Error: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=502)
        except ProductRegistrationError as e:
            logger.error(f"Product Registration Error: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=500)
        except EntityNotFound as e:
            logger.error(f"Entity Not Found: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=404)
        except InvalidCredentialsException as e:
            logger.error(f"Invalid Credentials Exception: {str(e)}")
            response = JSONResponse({"detail": str(e)}, status_code=403)
        except Exception as e:
            logger.error(f"Unexpected Exception: {str(e)}")
            response = JSONResponse(
                {"detail": "An unexpected error occurred"}, status_code=500
            )
        return response


app = FastAPI()

app.add_middleware(ExceptionMiddleware)
