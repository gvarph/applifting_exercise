from fastapi import FastAPI

from .background import OfferWorker

from .middleware import ExceptionMiddleware


from .endpoints import products_router, auth_router


def start_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(ExceptionMiddleware)
    app.include_router(products_router)
    app.include_router(auth_router)

    return app


app = start_app()


@app.on_event("startup")
async def startup_event():
    OfferWorker.start()


@app.on_event("shutdown")
async def shutdown_event():
    OfferWorker.stop()
