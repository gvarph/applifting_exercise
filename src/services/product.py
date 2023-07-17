from typing import List
import uuid

from fastapi import APIRouter


from ..db import session_scope
from ..models import Fetch, Offer, Product, offer_fetch
from ..schemas import (
    CreateProductModel,
    OfferModel,
    OfferPriceDiff,
    OfferPriceSummary,
    ProductModel,
)
from ..offers import fetch_products, register_product
from ..logger import get_logger
from ..errors import CustomException, EntityNotFound, ProductRegistrationError

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
            raise CustomException(message="Invalid product")
        with session_scope() as session:
            db_product: Product = Product(name=data.name, description=data.description)
            session.add(db_product)
            session.commit()

            session.refresh(db_product)

            try:
                await register_product(db_product, session)
            except Exception:
                raise ProductRegistrationError(message="Product registration failed")

            await fetch_products(db_product, session)

            product_model = ProductModel.from_product(db_product)

        return product_model

    async def update_product(
        self, product_id: uuid.UUID, new_product: CreateProductModel
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
                raise EntityNotFound(message="Product not found")

            product_model = ProductModel.from_product(db_product)
        return product_model

    async def delete_product(self, product_id: uuid.UUID):
        with session_scope() as session:
            # Find fetches for the product
            fetches = session.query(Fetch).filter(Fetch.product_id == product_id).all()

            # Delete offer-fetch associations for these fetches
            for fetch in fetches:
                for offer in fetch.offers:
                    session.execute(
                        offer_fetch.delete().where(
                            (offer_fetch.c.fetch_id == fetch.id)
                            & (offer_fetch.c.offer_id == offer.id)
                        )
                    )

            # Now you can safely delete the fetches
            session.query(Fetch).filter(Fetch.product_id == product_id).delete()

            session.commit()

            delete_stmt = (
                session.query(Product).filter(Product.id == product_id).delete()
            )

            if not delete_stmt:
                raise EntityNotFound(message="Product not found")

            session.commit()
        return

    async def get_offers(self, product_id: uuid.UUID) -> list[OfferModel]:
        with session_scope() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise EntityNotFound(message="Product not found")

            last_fetch_of_product = (
                session.query(Fetch)
                .filter(Fetch.product_id == product_id)
                .order_by(Fetch.time.desc())
                .first()
            )

            if not last_fetch_of_product:
                raise CustomException(message="No offers found")

            last_fetch = max(product.fetches, key=lambda f: f.time)

            offers: List[Offer] = last_fetch.offers

            models = [OfferModel.from_offer(offer, product_id) for offer in offers]

            return models

    async def get_price_history(
        self, product_id: str, from_time: float, to_time: float
    ) -> list[OfferPriceSummary]:
        with session_scope() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise EntityNotFound(message="Product not found")

            fetches = (
                session.query(Fetch)
                .filter(Fetch.product_id == product_id)
                .filter(Fetch.time >= from_time)
                .filter(Fetch.time <= to_time)
                .order_by(Fetch.time.desc())
                .all()
            )

            calculated_prices = [
                OfferPriceSummary.from_model(fetch.calculate_summary())
                for fetch in fetches
            ]

            return calculated_prices

    async def get_price_change(
        self, product_id: str, from_time: float, to_time: float
    ) -> OfferPriceDiff:
        with session_scope() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise EntityNotFound(message="Product not found")

            # Get the last fetch before the from_time
            last_fetch_before_from_time = (
                session.query(Fetch)
                .filter(Fetch.product_id == product_id)
                .filter(Fetch.time <= from_time)
                .order_by(Fetch.time.desc())
                .first()
            )

            # throw error if no fetch before from_time
            if not last_fetch_before_from_time:
                raise CustomException(message="No fetch before the specified time")

            # Get the last fetch before the to_time

            last_fetch_before_to_time = (
                session.query(Fetch)
                .filter(Fetch.product_id == product_id)
                .filter(Fetch.time <= to_time)
                .order_by(Fetch.time.desc())
                .first()
            )

            # throw error if the last fetch before to_time is the same as the last fetch before from_time
            if last_fetch_before_from_time.id == last_fetch_before_to_time.id:
                raise CustomException(message="No fetch before the specified time")

            # Get the offer summaries for for both fetches
            start_summary = last_fetch_before_from_time.calculate_summary()
            end_summary = last_fetch_before_to_time.calculate_summary()

            return OfferPriceDiff.calculate(start_summary, end_summary)
