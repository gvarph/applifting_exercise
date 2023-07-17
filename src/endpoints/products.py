import uuid

from fastapi import APIRouter, Depends, Query

from ..auth import auth_wrapper
from ..schemas import (
    CreateProductModel,
    OfferModel,
    OfferPriceDiff,
    OfferPriceSummary,
    ProductModel,
)
from ..services.product import ProductService
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# unnecessary dependency injection. I've left it here to show that I know how to use it.
# It could have been useful for testing if these functions were complex enough to require mocking.
def get_product_service() -> ProductService:
    return ProductService()


@router.get("/products/", response_model=list[ProductModel], status_code=200)
async def read_products(
    service: ProductService = Depends(get_product_service),
) -> list[ProductModel]:
    """
    Get all products from the database.

    Returns:
    - list[ProductModel]: List of all products.

    """
    return await service.read_products()


@router.post("/products/", response_model=ProductModel, status_code=201)
async def create_product(
    data: CreateProductModel,
    username=Depends(auth_wrapper),
    service: ProductService = Depends(get_product_service),
) -> ProductModel:
    """
    Create a new product and register it.

    Parameters:
    - data (CreateProductModel): Data of the product to create.

    Returns:
    - ProductModel: The created product.

    Raises:
    - CustomException: If the product data is invalid.
    - ProductRegistrationError: If the product registration failed.
    """
    return await service.create_product(data)


@router.put("/products/{product_id}", status_code=200)
async def update_product(
    product_id: uuid.UUID,
    new_product: ProductModel,
    username=Depends(auth_wrapper),
    service: ProductService = Depends(get_product_service),
) -> ProductModel:
    """
    Update an existing product.

    Parameters:
    - product_id (uuid.UUID): ID of the product to update.
    - new_product (ProductModel): New data for the product.

    Returns:
    - ProductModel: The updated product.

    Raises:
    - EntityNotFound: If the product does not exist.
    """
    return await service.update_product(product_id, new_product)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: uuid.UUID,
    user=Depends(auth_wrapper),
    service: ProductService = Depends(get_product_service),
):
    """
    Delete a product.

    Parameters:
    - product_id (uuid.UUID): ID of the product to delete.

    Raises:
    - EntityNotFound: If the product does not exist.
    """

    return await service.delete_product(product_id)


@router.get(
    "/products/{product_id}/offers", status_code=200, response_model=list[OfferModel]
)
async def get_offers(
    product_id: uuid.UUID,
    service: ProductService = Depends(get_product_service),
) -> list[OfferModel]:
    """
    Get the offers for a product.

    Parameters:
    - product_id (uuid.UUID): ID of the product to get offers for.

    Returns:
    - list[OfferModel]: List of offers for the product.

    Raises:
    - EntityNotFound: If the product does not exist.
    - CustomException: If no offers are found.
    """

    return await service.get_offers(product_id)


@router.get(
    "/products/{product_id}/price-history",
    status_code=200,
    response_model=list[OfferPriceSummary],
)
async def get_price_history(
    product_id: uuid.UUID,
    from_time: int = Query(...),
    to_time: int = Query(...),
    service: ProductService = Depends(get_product_service),
) -> list[OfferPriceSummary]:
    """
    Get the price history of a product.

    Parameters:
    - product_id (str): ID of the product to get price history for.
    - from_time (float): Start time for the history.
    - to_time (float): End time for the history.

    Returns:
    - list[OfferPriceSummary]: List of price summaries for the product.

    Raises:
    - EntityNotFound: If the product does not exist.
    """
    logger.info(f"Getting price history for product {product_id}")

    # x = await time_coro(service.get_price_history, product_id, from_time, to_time)

    return await service.get_price_history(product_id, from_time, to_time)


@router.get(
    "/products/{product_id}/price-diff",
    status_code=200,
    response_model=OfferPriceDiff,
)
async def get_price_diff(
    product_id: uuid.UUID,
    from_time: int = Query(...),
    to_time: int = Query(...),
    service: ProductService = Depends(get_product_service),
) -> OfferPriceDiff:
    """
    Get the price change of a product within a time range.

    Parameters:
    - product_id (str): ID of the product to get price change for.
    - from_time (float): Start time for the change calculation.
    - to_time (float): End time for the change calculation.

    Returns:
    - OfferPriceDiff: Difference in price.

    Raises:
    - EntityNotFound: If the product does not exist.
    - CustomException: If there are no fetches before the specified times.
    """
    logger.info(f"Getting price history for product {product_id}")

    # x = await time_coro(service.get_price_history, product_id, from_time, to_time)

    x: OfferPriceDiff = await service.get_price_change(product_id, from_time, to_time)

    logger.info(f"Got price difference for product {product_id}: {x}")

    return x
