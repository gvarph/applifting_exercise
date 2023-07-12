import time
from typing import Optional
import httpx
import asyncio
import jwt
from psycopg2 import DatabaseError
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import InvalidTokenError

from models import JwtToken, Product
from db import Session
from consts import TOKEN_SECRET, API_URL


# TODO: make this a custom exception and move it to a separate file
class AuthenticationFailedError(Exception):
    """Exception raised for errors in the authentication process"""

    def __init__(self, message="Authentication Failed"):
        self.message = message
        super().__init__(self.message)


class InvalidJwtTokenError(Exception):
    """Exception raised for errors in decoding JWT token"""

    def __init__(self, message="Invalid JWT Token"):
        self.message = message
        super().__init__(self.message)


async def get_token() -> JwtToken:
    # Get token from db
    db_token = None
    try:
        with Session() as session:
            db_token: JwtToken | None = session.query(JwtToken).first()
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database query failed: {str(e)}")

    # Check if token is valid.
    # This may cause issues if the token expires between the check and the request arriving at the server.
    # One way to fix this is checking if the token expires in the next x milliseconds,
    # and if so, wait for the token to expire and then request a new one.
    if (
        db_token is not None
        and db_token.expiration is not None
        and db_token.expiration > time.time()
    ):
        return db_token

    print("Token is invalid, requesting new token")
    if db_token is not None:
        print("current time:", time.time())
        print("token expiration:", db_token.expiration)
        print("difference:", db_token.expiration - time.time())

    async with httpx.AsyncClient() as client:
        headers = {"bearer": TOKEN_SECRET}

        try:
            response = await client.post(
                url=API_URL + "/auth",
                headers=headers,
            )
        except httpx.HTTPError as e:
            raise httpx.HTTPError(f"HTTP request failed: {str(e)}")

        if response.status_code != 201:
            print(response.status_code)
            print(response.text)
            raise AuthenticationFailedError("Could not authenticate")

        body = response.json()
        access_token = body.get("access_token")

        if not access_token:
            raise AuthenticationFailedError("Could not authenticate")

        try:
            # decode token without verifying signature
            decoded_token = jwt.decode(
                access_token, algorithms=["HS256"], options={"verify_signature": False}
            )
            expiration = decoded_token.get("expires")
        except InvalidTokenError as e:
            raise InvalidJwtTokenError(f"JWT Token decoding failed: {str(e)}")

        new_token = JwtToken(
            token=access_token,
            expiration=expiration,
        )

        try:
            with Session() as session:
                # remove old token
                session.query(JwtToken).delete()
                # add new token
                session.add(new_token)
                session.commit()
                new_token = session.query(JwtToken).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to commit token to database: {str(e)}")

        return new_token


async def register_product(product: Product):
    jwt_token = await get_token()

    async with httpx.AsyncClient() as client:
        headers = {"bearer": jwt_token.token}

        response = await client.post(
            url=API_URL + "/products/register",
            json=product.to_dict(),
            headers=headers,
        )

        return response.json()


async def get_offers(product_id: str):
    jwt_token = await get_token()

    async with httpx.AsyncClient() as client:
        headers = {"bearer": jwt_token.token}

        response = await client.get(
            url=API_URL + "/products/" + product_id + "/offers",
            headers=headers,
        )

        return response.json()


if __name__ == "__main__":
    import uuid
    import asyncio

    for i in range(10):
        product = Product(
            name="Test product" + str(i),
            description="Test description" + str(i),
            id=uuid.uuid4(),
        )
        # dump all product info
        asyncio.run(register_product(product))
        print("Registered product", product.id)
        offers = asyncio.run(get_offers(str(product.id)))
        print("Offers for product", product.id, ":", offers)

        time.sleep(1)
