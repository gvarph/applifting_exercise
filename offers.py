import time
from typing import Optional
import httpx
import consts
import asyncio
import jwt

from models import Product


# TODO: make this a custom exception and move it to a separate file
class AuthenticationFailedError(Exception):
    """Exception raised for errors in the authentication process"""

    def __init__(self, message="Authentication Failed"):
        self.message = message
        super().__init__(self.message)


class JWTTokenSingleton:
    _token: Optional[str] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _expiration: Optional[int] = None

    @classmethod
    async def get_token(self) -> str:
        async with self._lock:
            if self._token is None:  # first time
                await self._generate_token()
            elif self._expiration < time.time():  # token expired
                print("token expired")
                await self._generate_token()

            # we should have a valid token by now
            return self._token

    @classmethod
    async def _generate_token(self) -> None:
        async with httpx.AsyncClient() as client:
            headers = {"bearer": consts.refresh_token_secret}

            response = await client.post(
                url=consts.base_url + "/auth",
                headers=headers,
            )

            if response.status_code == 201 and response.json().get("access_token"):
                token = response.json()["access_token"]
                self._token = token
                self._expiration = jwt.decode(
                    token, options={"verify_signature": False}
                )

                print("token:", self._token)
                print("expiration:", self._expiration)

            else:
                print(response.status_code)
                print(response.json())
                raise AuthenticationFailedError("Could not authenticate")


async def register_product(product: Product):
    jwt_token = await JWTTokenSingleton.get_token()

    async with httpx.AsyncClient() as client:
        headers = {"bearer": jwt_token}

        response = await client.post(
            url=consts.base_url + "/products/register",
            json=product.to_dict(),
            headers=headers,
        )

        print(response.status_code)
        print(response.json())
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
        # wait 1 minute
