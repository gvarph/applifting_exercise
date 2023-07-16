from typing import List
import uuid

from fastapi import HTTPException, APIRouter


from ..db import session_scope
from ..errors import ApiRequestError, AuthenticationFailedError, EntityNotFound
from ..models import (
    Fetch,
    Offer,
    Product,
)
from ..schemas import CreateProductModel, OfferModel, ProductModel
from ..offers import fetch_products, register_product
from ..util import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ProductService:
    async def read_products(self) -> list[ProductModel]:
        try:
            with session_scope() as session:
                all_products = session.query(Product).all()

                logger.info(f"Found {len(all_products)} products")
                # convert to ProductModel
                models = [
                    ProductModel.from_product(product) for product in all_products
                ]
            return models
        except Exception as e:
            logger.error(f"Error reading products: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def create_product(self, data: CreateProductModel) -> ProductModel:
        if not data.name or not data.description:
            raise HTTPException(status_code=400, detail="Invalid product")
        try:
            with session_scope() as session:
                # create product
                db_product: Product = Product(
                    name=data.name, description=data.description
                )

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
            logger.error(f"Error creating product: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def update_product(
        self, product_id: uuid.UUID, new_product: ProductModel
    ) -> ProductModel:
        try:
            with session_scope() as session:
                session.query(Product).filter(Product.id == product_id).update(
                    {
                        Product.name: new_product.name,
                        Product.description: new_product.description,
                    }
                )
                session.commit()

                db_product = (
                    session.query(Product).filter(Product.id == product_id).first()
                )

                if not db_product:
                    raise EntityNotFound("Product not found")

            return db_product
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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
            return

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_offers(
        self,
        product_id: uuid.UUID,
    ) -> list[OfferModel]:
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

                offers: List[Offer] = last_fetch.offers

                models = [OfferModel.from_offer(offer, product_id) for offer in offers]

                return models

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
