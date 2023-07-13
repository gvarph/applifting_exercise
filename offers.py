import time
from typing import Optional
import httpx
import jwt
from psycopg2 import DatabaseError
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import InvalidTokenError
from errors import (
    ApiRequestError,
    AuthenticationFailedError,
    InvalidJwtTokenError,
    OffersFetchError,
    ProductRegistrationError,
)

from models import JwtToken, Offer, Product
from db import Session
from env import TOKEN_SECRET, API_URL
from util import get_logger

logger = get_logger(__name__)


async def _fetch_token_from_db() -> Optional[JwtToken]:
    """
    Fetch the first JWT token from the database. If a SQLAlchemyError occurs, log the error and raise a DatabaseError.
    """
    try:
        with Session() as session:
            return session.query(JwtToken).first()
    except SQLAlchemyError as e:
        logger.error(f"Database query failed: {str(e)}")
        raise DatabaseError(f"Database query failed: {str(e)}") from e


def _is_token_valid(token: JwtToken) -> bool:
    """
    Check if the token is valid. A valid token is defined as not None, has a defined expiration, and the expiration time is in the future.
    This expects the token.expiration to be a UNIX timestamp.
    """
    return (
        token is not None
        and token.expiration is not None
        and token.expiration > time.time()
    )


async def _fetch_new_token_from_api() -> httpx.Response:
    """
    Fetch a new JWT token from the API.
    """
    async with httpx.AsyncClient() as client:
        headers = {"bearer": TOKEN_SECRET}

        try:
            return await client.post(
                url=API_URL + "/auth",
                headers=headers,
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise ApiRequestError(f"HTTP request failed: {str(e)}") from e


def _decode_token(token: str):
    """
    Decode the JWT token without verifying the signature.
    """
    try:
        # decode token without verifying signature
        # TODO: get it to work with verify_signature=True
        return jwt.decode(
            token, algorithms=["HS256"], options={"verify_signature": False}
        )
    except InvalidTokenError as e:
        logger.error(f"JWT Token decoding failed: {str(e)}")
        raise InvalidJwtTokenError(f"JWT Token decoding failed: {str(e)}") from e


async def _store_new_token_in_db(token) -> Optional[JwtToken]:
    """
    Store a new JWT token in the database. If a SQLAlchemyError occurs, log the error and raise a DatabaseError.
    """
    try:
        with Session() as session:
            # remove old token
            session.query(JwtToken).delete()
            # add new token
            session.add(token)
            # commit changes
            session.commit()
            return session.query(JwtToken).first()
    except SQLAlchemyError as e:
        logger.error(f"Failed to commit token to database: {str(e)}")
        raise DatabaseError(f"Failed to commit token to database: {str(e)}") from e


async def _get_valid_token() -> JwtToken:
    """
    Get a valid JWT token. If no valid token exists in the database, fetch a new one from the API.
    """
    # Get token from db
    db_token = await _fetch_token_from_db()

    if _is_token_valid(db_token):
        return db_token

    logger.info("There is no token or it's invalid, requesting new token")

    response = await _fetch_new_token_from_api()

    # if response.status_code != 201:
    if response.status_code != httpx.codes.CREATED:
        logger.error("Response status code: %s", response.status_code)
        logger.error("Response text: %s", response.text)
        raise AuthenticationFailedError("Could not authenticate")

    body = response.json()
    access_token = body.get("access_token")

    if not access_token:
        raise AuthenticationFailedError("Could not authenticate")

    decoded_token = _decode_token(access_token)
    expiration = decoded_token.get("expires")

    new_token = JwtToken(
        token=access_token,
        expiration=expiration,
    )

    return await _store_new_token_in_db(new_token)


async def register_product(product: Product) -> None:
    """
    Register a product using the JWT token for authorization. If an error occurs during the HTTP request, log the error and return None.
    """
    jwt_token: JwtToken = await _get_valid_token()

    async with httpx.AsyncClient() as client:
        headers = {"bearer": jwt_token.token}

        try:
            response = await client.post(
                url=API_URL + "/products/register",
                json=product.to_dict(),
                headers=headers,
            )
        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise ProductRegistrationError(
                f"HTTP error occurred during product registration: {http_err}"
            ) from http_err
        except Exception as err:
            logger.error(f"An error occurred: {err}")
            raise ProductRegistrationError(
                f"An unexpected error occurred during product registration: {err}"
            ) from err

        # if response.status_code != 200:
        if response.status_code != httpx.codes.OK:
            logger.error(f"Unsuccessful request, status code: {response.status_code}")
            raise ProductRegistrationError(
                f"Unsuccessful product registration, status code: {response.status_code}"
            )

        logger.info(
            f"Product registration successful, status code: {response.status_code}"
        )


async def _fetch_product_offers_from_api(
    jwt_token: JwtToken, product_id: str
) -> httpx.Response:
    """
    Fetch offers for a specific product from the API.
    """
    async with httpx.AsyncClient() as client:
        headers = {"bearer": jwt_token.token}

        try:
            return await client.get(
                url=API_URL + "/products/" + product_id + "/offers",
                headers=headers,
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise OffersFetchError(f"HTTP request failed: {str(e)}") from e


def _process_response_and_create_offers(
    response: httpx.Response, product_id: str
) -> list[Offer]:
    """
    Process the response from the API and create Offer objects.
    """
    body = response.json()

    new_offers = []
    for offer in body:
        new_offer = Offer(
            price=offer.get("price"),
            id=offer.get("id"),
            items_in_stock=offer.get("items_in_stock"),
            product_id=product_id,
        )
        new_offers.append(new_offer)

    return new_offers


def _store_offers_in_db(offers) -> None:
    """
    Store offers in the database. If a SQLAlchemyError occurs, log the error and raise a DatabaseError.
    """
    try:
        with Session() as session:
            session.add_all(offers)
            session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Failed to commit offers to database: {str(e)}")
        raise DatabaseError(f"Failed to commit offers to database: {str(e)}") from e


async def get_offers(product_id: str) -> list[Offer]:
    """
    Get offers for a specific product. This includes fetching the offers from the API, processing the response, and storing the offers in the database.
    """
    jwt_token = await _get_valid_token()
    response = await _fetch_product_offers_from_api(jwt_token, product_id)
    new_offers = _process_response_and_create_offers(response, product_id)
    _store_offers_in_db(new_offers)

    return new_offers
