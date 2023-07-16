from typing import Optional
import uuid

from pydantic import BaseModel

from .models import Offer, Product
from .util import get_logger

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
    time: int
    min: float
    max: float
    avg: float
    median: float
    count: int
