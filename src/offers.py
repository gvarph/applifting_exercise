import asyncio
import time
from typing import List, Optional
import uuid
from fastapi import Response
import httpx
import jwt
from psycopg2 import DatabaseError
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import InvalidTokenError

from .errors import (
    ApiRequestError,
    AuthenticationFailedError,
    InvalidJwtTokenError,
    OffersFetchError,
    ProductRegistrationError,
)
from .models import Fetch, JwtToken, Offer, OfferModel, Product
from .db import Session, session_scope
import src.env as env
from .util import get_logger

logger = get_logger(__name__)


async def _fetch_token_from_db(session: Session) -> Optional[JwtToken]:
    """
    Fetch the first JWT token from the database. If a SQLAlchemyError occurs, log the error and raise a DatabaseError.

    Returns:
        Optional[JwtToken]: Returns the first JWT token found in the database or None if no token is found.
    """
    try:
        return session.query(JwtToken).first()
    except SQLAlchemyError as e:
        logger.error(f"Database query failed: {str(e)}")
        raise DatabaseError(f"Database query failed: {str(e)}") from e


def _is_token_valid(token: JwtToken) -> bool:
    """
    Check if the token is valid. A valid token is defined as not None, has a defined expiration, and the expiration time is in the future.
    This expects the token.expiration to be a UNIX timestamp and assumes that the endpoint accounts for clock skew.

    Args:
        token (JwtToken): JWT token object to be checked.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    return (
        token is not None
        and token.expiration is not None
        and token.expiration > time.time()
    )


async def _fetch_new_token_from_api() -> str:
    """
    Fetch a new JWT token from the API.

    Returns:
        str: The JWT token.
    """

    async with httpx.AsyncClient() as client:
        headers = {"Bearer": env.TOKEN_SECRET}

        url = env.API_URL + "/auth"
        try:
            logger.debug(f"fetching new token from {url}")
            response = await client.post(
                url=url,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                logger.error(f"Authentication failed: {e}")
                raise AuthenticationFailedError(response.json()["detail"])
            else:
                logger.error(f"HTTP request failed: {e}")
                raise ApiRequestError(f"HTTP request failed: {str(e)}") from e

        except httpx.HTTPError as e:
            logger.error(f"HTTP request failed: {e}")
            raise ApiRequestError(f"HTTP request failed: {str(e)}") from e

    body = response.json()

    if not "access_token" in body:
        raise ApiRequestError("Response does not contain access token")

    access_token = body["access_token"]

    logger.debug(f"new token: {access_token}")

    return access_token


def _decode_token(token: str):
    """
    Decode the JWT token without verifying the signature.

    Args:
        token (str): JWT token string to be decoded.

    Returns:
        dict: Decoded JWT token data.
    """
    try:
        # decode token without verifying signature - we don't have the secret as it's stored on the API
        decoded = jwt.decode(
            token, algorithms=["HS256"], options={"verify_signature": False}
        )
        return decoded

    except InvalidTokenError as e:
        logger.error(f"JWT Token decoding failed: {str(e)}")
        raise InvalidJwtTokenError(f"JWT Token decoding failed: {str(e)}") from e
    except Exception as e:
        logger.error(f"JWT Token decoding failed: {str(e)}")
        raise InvalidJwtTokenError(f"JWT Token decoding failed: {str(e)}") from e


async def _store_new_token_in_db(
    token: JwtToken, session: Session
) -> Optional[JwtToken]:
    """
    Store a new JWT token in the database. If the token already exists, update its value.
    If a SQLAlchemyError occurs, log the error and raise a DatabaseError.

    Args:
        token (JwtToken): JWT token object to be stored or updated in the database.

    Returns:
        Optional[JwtToken]: Returns the JWT token stored or updated in the database or None if the operation was not successful.
    """
    try:
        existing_token = session.query(JwtToken).first()
        if existing_token:
            existing_token.expiration = token.expiration
            existing_token.token = token.token
        else:
            session.add(token)
        session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Failed to commit token to database: {str(e)}")
        raise DatabaseError(f"Failed to commit token to database: {str(e)}") from e


async def _get_valid_token(session: Session) -> JwtToken:
    """
    Get a valid JWT token. If no valid token exists in the database, fetch a new one from the API.

    Returns:
        JwtToken: A valid JWT token.
    """
    # Get token from db
    db_token = await _fetch_token_from_db(session)

    if _is_token_valid(db_token):
        return db_token

    logger.info("There is no token or it's invalid, requesting new token")

    access_token = await _fetch_new_token_from_api()

    if not access_token:
        raise AuthenticationFailedError("Could not authenticate")

    decoded_token = _decode_token(access_token)
    expiration = decoded_token.get("expires")

    new_token = JwtToken(
        token=access_token,
        expiration=expiration,
    )

    logger.debug(f"{new_token=}")

    await _store_new_token_in_db(new_token, session)

    return new_token


async def register_product(product: Product, session: Session) -> None:
    """
    Register a product using the JWT token for authorization. If an error occurs during the HTTP request, log the error and return None.

    Args:
        product (Product): The product object to be registered.
    """
    jwt_token = await _get_valid_token(session)

    logger.debug(f"{jwt_token=}")

    async with httpx.AsyncClient() as client:
        headers = {"bearer": jwt_token.token}

        try:
            response = await client.post(
                url=env.API_URL + "/products/register",
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

        if not httpx.codes.is_success(response.status_code):
            logger.error(
                f"Unsuccessful request, status code: {response.status_code}\n Error: {response.text}"
            )

            raise ProductRegistrationError(
                f"Unsuccessful product offer registration, status code: {response.status_code}"
            )

        logger.info(f"Product {product.id} registered successfully")


async def _fetch_product_offers_from_api(
    jwt_token: JwtToken, product_id: str
) -> httpx.Response:
    """
    Fetch offers for a specific product from the API.

    Args:
        jwt_token (JwtToken): A valid JWT token object for authorization.
        product_id (str): The ID of the product to fetch the offers for.

    Returns:
        httpx.Response: Response object from the API call.
    """
    async with httpx.AsyncClient() as client:
        headers = {"bearer": jwt_token.token}

        try:
            return await client.get(
                url=env.API_URL + "/products/" + str(product_id) + "/offers",
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

    Args:
        response (httpx.Response): The response object from the API call.
        product_id (str): The ID of the product for which the offers are to be created.

    Returns:
        list[Offer]: A list of Offer objects created from the response data.
    """
    body = response.json()

    # if body = {'detail': 'Product does not exist'} than return empty list
    if "detail" in body and body["detail"] == "Product does not exist":
        return []

    new_offers = [
        Offer(
            price=offer["price"],
            id=offer["id"],
            items_in_stock=offer["items_in_stock"],
            product_id=product_id,
        )
        for offer in body
    ]

    return new_offers


def _store_offers_in_db(offers: list[Offer], product: Product, session) -> None:
    """
    Store offers in the database. If a SQLAlchemyError occurs, log the error and raise a DatabaseError.

    Args:
        offers (list[Offer]): A list of Offer objects to be stored in the database.
        product (Product): The product object for which the offers are to be stored.
    """
    try:
        with session_scope() as session:
            # refresh product
            product = session.query(Product).filter(Product.id == product.id).first()

            # Create a new fetch
            new_fetch = Fetch(
                id=uuid.uuid4(),
                time=time.time(),
            )
            product.fetches.append(new_fetch)

            session.add(new_fetch)

            session.commit()

    except SQLAlchemyError as e:
        logger.error(f"Failed to commit offers to database: {str(e)}")
        raise DatabaseError(f"Failed to commit offers to database: {str(e)}") from e


async def fetch_products(product: Product, session: Session) -> list[Offer]:
    """
    Get offers for a specific product. This includes fetching the offers from the API, processing the response, and storing the offers in the database.

    Args:
        product (Product): The product object for which the offers are to be fetched.

    Returns:
        list[Offer]: A list of Offer objects fetched from the API.
    """
    logger.info(f"Fetching offers for product {product.id}")

    with session_scope() as session:
        jwt_token = await _get_valid_token(session)
        response = await _fetch_product_offers_from_api(jwt_token, product.id)

        new_offers = _process_response_and_create_offers(response, product.id)
        _store_offers_in_db(new_offers, product, session)

    return new_offers
