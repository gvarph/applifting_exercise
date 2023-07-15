import asyncio
import uuid

from fastapi import FastAPI, HTTPException, status

from .background import OfferWorker

from .errors import ApiRequestError, AuthenticationFailedError

from .offers import fetch_products, register_product

from .db import Session, session_scope
from .models import (
    CreateProductModel,
    Fetch,
    OfferModel,
    Product,
    ProductModel,
)

app = FastAPI()

from .util import get_logger

logger = get_logger(__name__)


@app.on_event("startup")
async def startup_event():
    OfferWorker.start()


@app.on_event("shutdown")
async def shutdown_event():
    OfferWorker.stop()


@app.get("/products/", response_model=list[ProductModel], status_code=200)
async def read_products():
    try:
        with session_scope() as session:
            all_products = session.query(Product).all()

        # convert to ProductModel
        models = [
            ProductModel(
                id=product.id, name=product.name, description=product.description
            )
            for product in all_products
        ]
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/products/", response_model=ProductModel, status_code=201)
async def create_product(data: CreateProductModel) -> ProductModel:
    if not data.name or not data.description:
        raise HTTPException(status_code=400, detail="Invalid product")
    try:
        with session_scope() as session:
            # create product
            db_product: Product = Product(name=data.name, description=data.description)

            # persist product
            session.add(db_product)
            session.commit()
            session.refresh(db_product)

            await register_product(db_product, session)

            # fetch offers for the first time
            await fetch_products(db_product, session)

            product_model = ProductModel.from_product(db_product)

        return product_model
    except AuthenticationFailedError as e:
        logger.error(f"Offer API Authentication failed: {e}")
        raise HTTPException(
            status_code=400, detail=f"Offer API authentication failed: {e}"
        )
    except ApiRequestError as e:
        logger.error(f"Error in offers service: {e}")
        raise HTTPException(
            status_code=500, detail="Communication with offers service failed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/products/{product_id}", status_code=200)
async def update_product(product_id: uuid.UUID, new_product: ProductModel):
    try:
        with session_scope() as session:
            session.query(Product).filter(Product.id == product_id).update(
                {
                    Product.name: new_product.name,
                    Product.description: new_product.description,
                }
            )
            session.commit()

            # TODO: update product in offers service?
            db_product = session.query(Product).filter(Product.id == product_id).first()
        print(db_product)
        return db_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: uuid.UUID):
    try:
        with session_scope() as session:
            delete_stmt = (
                session.query(Product).filter(Product.id == product_id).delete()
            )

            if not delete_stmt:
                raise HTTPException(status_code=404, detail="Product not found")
            session.commit()
            # TODO: delete product in offers service?
        return status.HTTP_204_NO_CONTENT

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/products/{product_id}/offers", status_code=200, response_model=list[OfferModel]
)
async def get_offers(
    product_id: uuid.UUID,
) -> list[OfferModel]:
    logger.debug(f"Getting offers for product {product_id}")
    try:
        with session_scope() as session:
            # check if product exists
            product: Product | None = (
                session.query(Product).filter(Product.id == product_id).first()
            )
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            last_fetch_of_product: Fetch | None = (
                session.query(Fetch)
                .where(Fetch.product_id == product_id)
                .order_by(Fetch.time.desc())
                .first()
            )

            if not last_fetch_of_product:
                # We know the product exists, but there are no offers for it
                raise HTTPException(status_code=404, detail="No offers found")

            fetches_on_product = product.fetches

            # get fetch with highest time
            last_fetch = max(fetches_on_product, key=lambda f: f.time)

            logger.debug(f"Last fetch: {last_fetch}")

            offers = last_fetch.offers

            models = [OfferModel.from_offer(offer) for offer in offers]

            return models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
