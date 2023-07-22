import json
from unittest.mock import patch
import uuid
from fastapi.testclient import TestClient
import pytest
from src.auth import auth_wrapper
from src.main import app
from src.pydantic_models import CreateProductModel, OfferPriceDiff, ProductModel
from src.services import ProductService

client = TestClient(app)

test_price_diff = OfferPriceDiff(
    min=1.0,
    max=2.0,
    avg=1.5,
    median=1.5,
)
id = uuid.uuid4()


class MockProductService:
    async def read_products(self):
        # Predefined data to return when mocked method is called
        return [ProductModel(id=uuid.uuid4(), name="test", description="test")]

    async def create_product(self, data: CreateProductModel):
        # Predefined data to return when mocked method is called
        return ProductModel(
            id=uuid.uuid4(), name=data.name, description=data.description
        )

    async def get_price_change(self, product_id: str, from_time: float, to_time: float):
        return test_price_diff


async def auth_wrapper_override(token: str = "token"):
    return "johndoe"


app.dependency_overrides[auth_wrapper] = auth_wrapper_override


def test_create_product():
    with patch.object(
        ProductService, "create_product", MockProductService.create_product
    ):
        response = client.post(
            "/products/",
            json={"name": "Test Product", "description": "This is a test product"},
            headers={"Bearer": "Bearer fake_jwt"},
        )

    assert response.status_code == 201
    assert response.json() == {
        "id": response.json()["id"],
        "name": "Test Product",
        "description": "This is a test product",
    }


def test_read_products():
    with patch.object(
        ProductService, "read_products", MockProductService.read_products
    ):
        response = client.get(
            "/products/", headers={"Authorization": "Bearer fake_jwt"}
        )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == {
        "id": response.json()[0]["id"],
        "name": "test",
        "description": "test",
    }


def test_get_price_diff_valid():
    with patch.object(
        ProductService, "get_price_change", MockProductService.get_price_change
    ):
        response = client.get(
            f"/products/{id}/price-diff", params={"from_time": 1.0, "to_time": 2.0}
        )

    assert response.status_code == 200
    assert response.json() == json.loads(test_price_diff.model_dump_json())


def test_get_price_diff_invalid_times():
    with patch.object(
        ProductService, "get_price_change", MockProductService.get_price_change
    ):
        response = client.get(
            f"/products/{id}/price-diff", params={"from_time": 2.0, "to_time": 1.0}
        )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Start time cannot be greater than end time",
    }


def test_get_price_diff_valid():
    with patch.object(
        ProductService, "get_price_change", MockProductService.get_price_change
    ):
        response = client.get(
            f"/products/{id}/price-diff", params={"from_time": 1.0, "to_time": 2.0}
        )

    assert response.status_code == 200
    assert response.json() == json.loads(test_price_diff.model_dump_json())


def test_get_price_diff_422():
    with patch.object(
        ProductService, "get_price_change", MockProductService.get_price_change
    ):
        response = client.get(
            f"/products/{id}/price-diff", params={"from_time": "a", "to_time": "b"}
        )

    assert response.status_code == 422
