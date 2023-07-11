from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base

import db

Base = declarative_base()


@dataclass(slots=True)
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID, primary_key=True)
    name = Column(String)
    description = Column(String)


@dataclass(slots=True)
class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID, primary_key=True)
    price = Column(Integer)
    items_in_stock = Column(Integer)
    product_id = Column(UUID, ForeignKey("products.id"))


Base.metadata.create_all(db.engine)
