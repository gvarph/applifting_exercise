from uuid import uuid4

import pytest
from src.models import (
    CreateProductModel,
    JwtToken,
    Offer,
    OfferModel,
    Product,
    ProductModel,
)


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
    product_model = ProductModel(id=uuid4(), name="test", description="test")
    assert product_model.to_product() == Product(
        id=product_model.id,
        name=product_model.name,
        description=product_model.description,
    )


def test_jwtToken_to_str():
    jwt_token = JwtToken(token="test", expiration=1234)
    assert (
        str(JwtToken(token="test", expiration=1234))
        == f"<JwtToken(token={jwt_token.token}, expiration={jwt_token.expiration})>"
    )


def test_createModelProduct_toProduct():
    createModelProduct = CreateProductModel(name="test", description="test")
    modelProduct = createModelProduct.to_product()
    assert modelProduct.name == createModelProduct.name
    assert modelProduct.description == createModelProduct.description
    assert modelProduct.id is not None


""" def test_offerModel_toOffer():
    offerModel = OfferModel(
        id=uuid4(), price=1234, items_in_stock=1234, product_id=uuid4()
    )
    assert offerModel.toOffer() == Offer(
        id=offerModel.id,
        price=offerModel.price,
        items_in_stock=offerModel.items_in_stock,
        product_id=offerModel.product_id,
    ) #TODO: fix this test
 """
