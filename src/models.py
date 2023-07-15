from dataclasses import dataclass
from typing import Optional
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import declarative_base

from pydantic import BaseModel


from . import db


Base = declarative_base()


@dataclass
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)

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

    def toProduct(self):
        return Product(
            id=uuid.uuid4(),
            name=self.name,
            description=self.description,
        )


class ProductModel(CreateProductModel):
    id: uuid.UUID

    def toProduct(self):
        return Product(
            id=self.id,
            name=self.name,
            description=self.description,
        )


@dataclass
class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = Column(Integer)
    items_in_stock = Column(Integer)
    product_id = Column(UUID, ForeignKey("products.id"))


class OfferModel(BaseModel):
    id: uuid.UUID
    price: int
    items_in_stock: int
    product_id: uuid.UUID

    def toOffer(self):
        return Offer(
            id=self.id,
            price=self.price,
            items_in_stock=self.items_in_stock,
            product_id=self.product_id,
        )


@dataclass
class JwtToken(Base):
    __tablename__ = "jwt_tokens"

    token = Column(String, primary_key=True)
    expiration = Column(Integer)

    def __repr__(self):
        return f"<JwtToken(token={self.token}, expiration={self.expiration})>"


Base.metadata.create_all(db.engine)
