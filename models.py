from dataclasses import dataclass
from typing import Optional
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base

from pydantic import BaseModel


import db


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


class ProductModel(BaseModel):
    name: str
    description: str
    id: Optional[uuid.UUID] = None


class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = Column(Integer)
    items_in_stock = Column(Integer)
    product_id = Column(UUID, ForeignKey("products.id"))


Base.metadata.create_all(db.engine)
