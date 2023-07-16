from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException


from ..errors import (
    AuthenticationFailedError,
    InvalidJwtTokenError,
    ApiRequestError,
    OffersFetchError,
    ProductRegistrationError,
    EntityNotFound,
    InvalidCredentialsException,
)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except StarletteHTTPException as e:
            response = JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except AuthenticationFailedError as e:
            response = JSONResponse({"detail": str(e)}, status_code=401)
        except InvalidJwtTokenError as e:
            response = JSONResponse({"detail": str(e)}, status_code=401)
        except ApiRequestError as e:
            response = JSONResponse({"detail": str(e)}, status_code=502)
        except OffersFetchError as e:
            response = JSONResponse({"detail": str(e)}, status_code=502)
        except ProductRegistrationError as e:
            response = JSONResponse({"detail": str(e)}, status_code=500)
        except EntityNotFound as e:
            response = JSONResponse({"detail": str(e)}, status_code=404)
        except InvalidCredentialsException as e:
            response = JSONResponse({"detail": str(e)}, status_code=403)
        except Exception as e:
            response = JSONResponse(
                {"detail": "An unexpected error occurred"}, status_code=500
            )
        return response


app = FastAPI()

app.add_middleware(ExceptionMiddleware)
