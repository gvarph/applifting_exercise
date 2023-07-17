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
    Read all products from the database and returns them as ProductModels.

    Raises:
        HTTPException: if an unexpected error occurs during the operation.

    Returns:
        list[ProductModel]: A list of product model objects.
    """
    return await service.read_products()


@router.post("/products/", response_model=ProductModel, status_code=201)
async def create_product(
    data: CreateProductModel,
    username=Depends(auth_wrapper),
    service: ProductService = Depends(get_product_service),
) -> ProductModel:
    """
    Create a new product and persists it in the database.

    Args:
        data (CreateProductModel): The model containing the details of the product to create.

    Raises:
        HTTPException: If the product details are invalid or if an unexpected error occurs during the operation.

    Returns:
        ProductModel: The created product as a ProductModel object.
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
    Update an existing product in the database.

    Args:
        product_id (uuid.UUID): The ID of the product to update.
        new_product (ProductModel): The model containing the updated details of the product.

    Raises:
        HTTPException: If an unexpected error occurs during the operation.

    Returns:
        ProductModel: The updated product as a ProductModel object.
    """
    return await service.update_product(product_id, new_product)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: uuid.UUID,
    user=Depends(auth_wrapper),
    service: ProductService = Depends(get_product_service),
):
    """
    Delete a product from the database.

    Args:
        product_id (uuid.UUID): The ID of the product to delete.

    Raises:
        HTTPException: If the product is not found or if an unexpected error occurs during the operation.
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
    Get all offers for a particular product from the database.

    Args:
        product_id (uuid.UUID): The ID of the product for which to fetch the offers.

    Raises:
        HTTPException: If the product is not found, no offers are found for it, or if an unexpected error occurs during the operation.

    Returns:
        list[OfferModel]: A list of offer model objects for the product.
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
    Get the price history for a particular product from the database.

    Args:
        product_id (uuid.UUID): The ID of the product for which to fetch the price history.
        from_time (int): The start of the time range for which to fetch the price history in unix epoch time.
        to_time (int): The end of the time range for which to fetch the price history in unix epoch time.

    Returns:
        list[OfferPriceSummary]: A list of offer price summary objects for the product.
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
    Get the price history for a particular product from the database.

    Args:
        product_id (uuid.UUID): The ID of the product for which to fetch the price history.

        from_time (int): The start of the time range for which to fetch the price history in unix epoch time.
        to_time (int): The end of the time range for which to fetch the price history in unix epoch time.

    Returns:
        OfferPriceDiff: The procentual price differences between the first and last offers in the time range
    """
    logger.info(f"Getting price history for product {product_id}")

    # x = await time_coro(service.get_price_history, product_id, from_time, to_time)

    x: OfferPriceDiff = await service.get_price_change(product_id, from_time, to_time)

    logger.info(f"Got price difference for product {product_id}: {x}")

    return x
