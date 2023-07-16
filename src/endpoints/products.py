from typing import List
import uuid

from fastapi import HTTPException, APIRouter, Depends

from ..services.product import ProductService


from ..auth import auth_wrapper
from ..db import session_scope
from ..errors import ApiRequestError, AuthenticationFailedError
from ..models import (
    Fetch,
    Offer,
    Product,
)
from ..schemas import CreateProductModel, OfferModel, ProductModel
from ..offers import fetch_products, register_product
from ..util import get_logger

logger = get_logger(__name__)

router = APIRouter()

from fastapi import Depends

service = ProductService()


@router.get("/products/", response_model=list[ProductModel], status_code=200)
async def read_products() -> list[ProductModel]:
    """
    Read all products from the database and returns them as ProductModels.

    Raises:
        HTTPException: if an unexpected error occurs during the operation.

    Returns:
        list[ProductModel]: A list of product model objects.
    """
    __doc__ = service.read_products.__doc__
    return await service.read_products()


@router.post("/products/", response_model=ProductModel, status_code=201)
async def create_product(
    data: CreateProductModel, username=Depends(auth_wrapper)
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
    product_id: uuid.UUID, new_product: ProductModel, username=Depends(auth_wrapper)
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
async def delete_product(product_id: uuid.UUID, username=Depends(auth_wrapper)):
    """
    Delete a product from the database.

    Args:
        product_id (uuid.UUID): The ID of the product to delete.
        username (str): The username of the user making the request.

    Raises:
        HTTPException: If the product is not found or if an unexpected error occurs during the operation.
    """

    return await service.delete_product(product_id)


@router.get(
    "/products/{product_id}/offers", status_code=200, response_model=list[OfferModel]
)
async def get_offers(
    product_id: uuid.UUID,
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
