import asyncio

from .models import Product
from .db import SessionMkr, session_scope
import src.env as env
from .logger import get_logger
from .offers import fetch_products

logger = get_logger(__name__)


# If we wanted to make this scalable, we should separate this into a separate microservice and use something like celery.


class OfferWorker:
    """
    A worker class responsible for periodically fetching offers for products.

    Attributes:
        _is_running (bool): Status flag indicating whether the worker is currently running.
    """

    _is_running = False

    @classmethod
    def start(cls):
        """
        Starts the OfferWorker. This initiates the periodic fetching of offers.
        """
        cls._is_running = True
        logger.debug("Starting OfferWorker")
        asyncio.create_task(cls.periodic_fetch_offers())

    @classmethod
    def stop(cls):
        """
        Stops the OfferWorker. This halts the periodic fetching of offers after the current iteration.
        """
        logger.debug("Stopping OfferWorker")
        cls._is_running = False  # will stop on the next iteration

    @classmethod
    async def periodic_fetch_offers(cls):
        """
        Periodically fetches offers for all products from the database. The fetching continues as long as
        the '_is_running' attribute is set to True. The interval between fetches is determined by the
        'PERIODIC_FETCH_INTERVAL' environmental variable. If '_is_running' is set to False, the fetching
        will stop after the current iteration.

        Note: This method is an asynchronous coroutine and must be awaited when called.
        """
        logger.debug("Starting periodic fetch")
        while cls._is_running:
            with session_scope() as session:
                products = session.query(Product).all()

                for product in products:
                    # await to make the load on the db and the api more even
                    await fetch_products(product, session)

            await asyncio.sleep(env.PERIODIC_FETCH_INTERVAL)
        logger.debug("Stopping periodic fetch")
