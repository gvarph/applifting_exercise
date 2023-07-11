import httpx

from models import Product
import consts


async def register_product(product: Product):
    async with httpx.AsyncClient() as client:
        headers = {"bearer": consts.refresh_token_secret}

        response = await client.post(
            url=consts.base_url + "/products/",
            json=product.dict(),
            headers=headers,
        )

        return response.json()
