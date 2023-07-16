import uuid
from dataclasses import dataclass
from typing import List

from sqlalchemy import Column, Float, Integer, String, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, Relationship

from . import db
from .errors import EntityNotFound
from .logger import get_logger


logger = get_logger(__name__)


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
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
)


@dataclass
class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = Column(Integer)
    items_in_stock = Column(Integer)
    product_id = Column(UUID, ForeignKey("products.id"))

    def __repr__(self):
        return f"<Offer(id={self.id}, price={self.price}, items_in_stock={self.items_in_stock})>"


@dataclass
class Fetch(Base):
    __tablename__ = "fetch"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    time = Column(Float)

    product_id = Column(UUID, ForeignKey("products.id"))


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


Offer.product: Relationship[Product] = relationship("Product", back_populates="offers")

Fetch.product: Relationship[Product] = relationship("Product", back_populates="fetches")

Fetch.offers: Relationship[List[Offer]] = relationship(
    "Offer", secondary=offer_fetch, cascade="all, delete"
)

Offer.fetches: Relationship[List[Fetch]] = relationship("Fetch", secondary=offer_fetch)


Base.metadata.create_all(db.engine)


def link_offer_to_fetch(offer: Offer, fetch: Offer, session: db.Session):
    offer = session.query(Offer).filter_by(id=offer.id).first()

    if offer and fetch:
        fetch.offers.append(offer)
    else:
        logger.debug("Offer or fetch not found")
        raise EntityNotFound("Offer or fetch not found")
