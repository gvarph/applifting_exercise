from fastapi import FastAPI

from .middleware.exception import ExceptionMiddleware


from .endpoints.products import router as products_router
from .endpoints.auth import router as auth_router


def start_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(ExceptionMiddleware)
    app.include_router(products_router)
    app.include_router(auth_router)

    return app


app = start_app()
