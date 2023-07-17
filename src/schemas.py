from typing import Optional
import uuid

from pydantic import BaseModel

from .models import Offer, OfferSummary, Product
from .logger import get_logger

logger = get_logger(__name__)


class OfferModel(BaseModel):
    id: uuid.UUID
    price: int
    items_in_stock: int
    product_id: uuid.UUID

    def to_offer(self):
        return Offer(
            id=self.id,
            price=self.price,
            items_in_stock=self.items_in_stock,
            # fetch=fetch,
        )

    @staticmethod
    def from_offer(offer: Offer, product_id: uuid.UUID):
        return OfferModel(
            id=offer.id,
            price=offer.price,
            items_in_stock=offer.items_in_stock,
            product_id=product_id,
        )


class CreateProductModel(BaseModel):
    name: str
    description: str

    def to_product(self):
        new_product = Product(
            name=self.name, description=self.description, id=uuid.uuid4()
        )

        return new_product


class ProductModel(CreateProductModel):
    id: uuid.UUID

    def to_product(self):
        return Product(
            id=self.id,
            name=self.name,
            description=self.description,
        )

    @staticmethod
    def from_product(product: Product):
        return ProductModel(
            id=product.id,
            name=product.name,
            description=product.description,
        )


class AuthModel(BaseModel):
    username: str
    password: str


class TokenModel(BaseModel):
    username: Optional[str] = None


class OfferPriceSummary(BaseModel):
    time: float
    min: float
    max: float
    avg: float
    median: float
    count: int

    @staticmethod
    def from_model(model: OfferSummary):
        return OfferPriceSummary(
            time=model.fetch.time,
            min=model.min_price,
            max=model.max_price,
            avg=model.avg_price,
            median=model.median_price,
            count=model.offer_count,
        )


class OfferPriceDiff(BaseModel):
    """
    Represents the percentage difference between prices for two different OfferSummaries
    """

    min: float
    max: float
    avg: float
    median: float

    @staticmethod
    def calculate(start: OfferSummary, end: OfferSummary) -> "OfferPriceDiff":
        """
        Calculate the percentage difference between two OfferSummaries
        """
        return OfferPriceDiff(
            min=(end.min_price - start.min_price) / start.min_price,
            max=(end.max_price - start.max_price) / start.max_price,
            avg=(end.avg_price - start.avg_price) / start.avg_price,
            median=(end.median_price - start.median_price) / start.median_price,
        )

    def __repr__(self):
        return f"OfferPriceDiff(min={self.min}, max={self.max}, avg={self.avg}, median={self.median})"

    def __str__(self):
        return self.__repr__()
