from unittest.mock import MagicMock, patch
from uuid import uuid4
from fastapi.testclient import TestClient

from src.models import Product
from src.main import app
from src.util import get_logger

client = TestClient(app)

logger = get_logger(__name__)


@patch("src.db.SessionMkr")
def test_valid(mock_session):
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

    response = client.get("/products")

    logger.info(response.json())
    assert response.status_code == 200

    assert response.json() == prod

    # Check the function is called
    mock_session.return_value.query.assert_called_once_with(Product)
    mock_query.all.assert_called_once()


@patch("src.db.SessionMkr")
def test_error(mock_session):
    mock_query = MagicMock()
    mock_query.all.side_effect = Exception("Test exception")

    # Make session.query(Product) return our mock query object
    mock_session.return_value.query.return_value = mock_query

    response = client.get("/products")

    assert response.status_code == 500
    assert response.json() == {"detail": "Test exception"}

    # Check the function is called
    mock_session.return_value.query.assert_called_once_with(Product)
    mock_query.all.assert_called_once()
