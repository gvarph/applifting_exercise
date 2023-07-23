from unittest.mock import MagicMock, patch
from uuid import uuid4
import pytest


from src.exceptions.external import ApiRequestError
from src.services.product import ProductService
from src.orm_models import Product
from src.logger import get_logger


@pytest.fixture
def service() -> ProductService:
    return ProductService()


logger = get_logger(__name__)


@pytest.mark.asyncio
@patch("src.db.SessionMkr")
async def test_valid(mock_session, service):
    prod = [
        {
            "id": str(uuid4()),
            "name": f"Test Product {i}",
            "description": f"This is a test product {i}.",
        }
        for i in range(10)
    ]

    mock_products = []
    for model in prod:
        mock_product = MagicMock()
        mock_product.id = model["id"]
        mock_product.name = model["name"]
        mock_product.description = model["description"]
        mock_products.append(mock_product)

    mock_query = MagicMock()
    mock_query.all.return_value = mock_products

    # Make session.query(Product) return our mock query object
    mock_session.return_value.query.return_value = mock_query

    data = await service.read_products()

    # Check the function is called
    mock_session.return_value.query.assert_called_once_with(Product)
    mock_query.all.assert_called_once()


@pytest.mark.asyncio
@patch("src.db.SessionMkr")
async def test_error(mock_session, service):
    mock_query = MagicMock()
    mock_query.all.side_effect = ApiRequestError("mock exc")

    # Make session.query(Product) return our mock query object
    mock_session.return_value.query.return_value = mock_query

    with pytest.raises(ApiRequestError):
        data = await service.read_products()

    # Check the function is called
    mock_session.return_value.query.assert_called_once_with(Product)
    mock_query.all.assert_called_once()
