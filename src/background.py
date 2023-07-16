import asyncio

from .models import Product
from .db import SessionMkr, session_scope
import src.env as env
from .logger import get_logger
from .offers import fetch_products

logger = get_logger(__name__)


class OfferWorker:
    _is_running = False

    @classmethod
    def start(cls):
        cls._is_running = True
        logger.debug("Starting OfferWorker")
        asyncio.create_task(cls.periodic_fetch_offers())

    @classmethod
    def stop(cls):
        logger.debug("Stopping OfferWorker")
        cls._is_running = False  # will stop on the next iteration

    @classmethod
    async def periodic_fetch_offers(cls):
        logger.debug("Starting periodic fetch")
        while cls._is_running:
            with session_scope() as session:
                products = session.query(Product).all()

                for product in products:
                    # await to make the load on the db and the api more even
                    await fetch_products(product, session)

            await asyncio.sleep(env.PERIODIC_FETCH_INTERVAL)
        logger.debug("Stopping periodic fetch")
