from ast import Tuple
from typing import List
import uuid

from fastapi import HTTPException, APIRouter


from ..db import session_scope
from ..errors import ApiRequestError, AuthenticationFailedError, EntityNotFound
from ..models import (
    Fetch,
    Offer,
    Product,
    offer_fetch,
)
from ..schemas import CreateProductModel, OfferModel, OfferPriceSummary, ProductModel
from ..offers import fetch_products, register_product
from ..util import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ProductService:
    async def read_products(self) -> list[ProductModel]:
        with session_scope() as session:
            all_products = session.query(Product).all()
            logger.info(f"Found {len(all_products)} products")
            models = [ProductModel.from_product(product) for product in all_products]
        return models

    async def create_product(self, data: CreateProductModel) -> ProductModel:
        if not data.name or not data.description:
            raise HTTPException(status_code=400, detail="Invalid product")
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

    async def update_product(
        self, product_id: uuid.UUID, new_product: ProductModel
    ) -> ProductModel:
        with session_scope() as session:
            session.query(Product).filter(Product.id == product_id).update(
                {
                    Product.name: new_product.name,
                    Product.description: new_product.description,
                }
            )
            session.commit()

            db_product = session.query(Product).filter(Product.id == product_id).first()

            if not db_product:
                raise EntityNotFound("Product not found")

        return db_product

    async def delete_product(product_id: uuid.UUID):
        with session_scope() as session:
            delete_stmt = (
                session.query(Product).filter(Product.id == product_id).delete()
            )

            if not delete_stmt:
                raise HTTPException(status_code=404, detail="Product not found")
            session.commit()
            # TODO: delete product in offers service?
        return

    async def get_offers(
        self,
        product_id: uuid.UUID,
    ) -> list[OfferModel]:
        with session_scope() as session:
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

    async def get_price_history(
        self, product_id: str, from_time: float, to_time: float
    ) -> list[OfferPriceSummary]:
        with session_scope() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise EntityNotFound("Product not found")

            fetches = (
                session.query(Fetch)
                .filter(Fetch.product_id == product_id)
                .filter(Fetch.time >= from_time)
                .filter(Fetch.time <= to_time)
                .order_by(Fetch.time.desc())
                .all()
            )

            calculated_prices: List[OfferPriceSummary] = []
            for fetch in fetches:
                offers = fetch.offers

                prices = [offer.price for offer in offers]

                summary = OfferPriceSummary(
                    time=fetch.time,
                    min=min(prices),
                    max=max(prices),
                    avg=sum(prices) / len(prices),
                    median=prices[len(prices) // 2],
                    count=len(prices),
                )

                calculated_prices.append(summary)

            return calculated_prices
