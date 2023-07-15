from dataclasses import dataclass
from typing import List
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import Column, Float, Integer, String, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import declarative_base, Mapped, Relationship

from pydantic import BaseModel


from . import db


Base = declarative_base()


@dataclass
class JwtToken(Base):
    __tablename__ = "jwt_tokens"

    token = Column(String, primary_key=True)
    expiration = Column(Integer)

    def __repr__(self):
        return f"<JwtToken(token={self.token}, expiration={self.expiration})>"


# Table for many-to-many relationship between offers and fetches
offer_fetch = Table(
    "offer_fetch",
    Base.metadata,
    Column("offer_id", UUID, ForeignKey("offers.id")),
    Column("fetch_id", UUID, ForeignKey("fetch.id")),
)


@dataclass
class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = Column(Integer)
    items_in_stock = Column(Integer)
    product_id = Column(UUID, ForeignKey("products.id"))


@dataclass
class Fetch(Base):
    __tablename__ = "fetch"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    time = Column(Float)

    product_id = Column(UUID, ForeignKey("products.id"))


class OfferModel(BaseModel):
    id: uuid.UUID
    price: int
    items_in_stock: int
    product_id: uuid.UUID

    def to_offer(self, fetch_batch: uuid.UUID):
        return Offer(
            id=self.id,
            price=self.price,
            items_in_stock=self.items_in_stock,
            fetch_batch=fetch_batch,
        )

    @staticmethod
    def from_offer(offer: Offer):
        return OfferModel(
            id=offer.id,
            price=offer.price,
            items_in_stock=offer.items_in_stock,
            product_id=offer.product_id,
        )


@dataclass
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)

    offers: Relationship[List[Offer]] = relationship(
        "Offer", back_populates="product", cascade="all, delete"
    )
    fetches: Relationship[List[Fetch]] = relationship(
        "Fetch", back_populates="product", cascade="all, delete"
    )

    def __repr__(self):
        return (
            f"<Product(id={self.id}, name={self.name}, description={self.description})>"
        )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
        }


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


Offer.product: Relationship[Product] = relationship("Product", back_populates="offers")

Fetch.product: Relationship[Product] = relationship("Product", back_populates="fetches")

Fetch.offers: Relationship[List[Offer]] = relationship(
    "Offer", secondary=offer_fetch, cascade="all, delete"
)


Base.metadata.create_all(db.engine)
