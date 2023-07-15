from uuid import uuid4

import pytest
from src.models import JwtToken, Product, ProductModel


@pytest.fixture
def product():
    return Product(id=uuid4(), name="test", description="test")


def test_product_to_str(product):
    assert (
        str(product)
        == f"<Product(id={product.id}, name={product.name}, description={product.description})>"
    )


def test_product_to_dict(product):
    assert product.to_dict() == {
        "id": str(product.id),
        "name": product.name,
        "description": product.description,
    }


def test_productModel_toProduct():
    productModel = ProductModel(id=uuid4(), name="test", description="test")
    assert productModel.toProduct() == Product(
        id=productModel.id, name=productModel.name, description=productModel.description
    )


def test_jwtToken_to_str():
    jwtToken = JwtToken(token="test", expiration=1234)
    assert (
        str(JwtToken(token="test", expiration=1234))
        == f"<JwtToken(token={jwtToken.token}, expiration={jwtToken.expiration})>"
    )
