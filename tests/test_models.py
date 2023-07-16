from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from src.models import (
    JwtToken,
    Product,
    link_offer_to_fetch,
)

from src.schemas import CreateProductModel, ProductModel


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
    product: Product = product_model.to_product()

    # does not have a proper comparison method so we have to compare each field

    assert product.id == product_model.id
    assert product.name == product_model.name
    assert product.description == product_model.description


def test_productModel_fromProduct():
    product = Product(id=uuid4(), name="test", description="test")
    product_model = ProductModel.from_product(product)

    # does not have a proper comparison method so we have to compare each field

    assert product.id == product_model.id
    assert product.name == product_model.name
    assert product.description == product_model.description


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


@patch("src.db.Session")
@patch("src.models.Offer")
def test_link_offer_to_fetch_success(mock_offer, mock_session):
    mock_offer_instance = Mock()
    mock_fetch_instance = Mock()
    mock_offer.id = 1
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_offer_instance
    )

    link_offer_to_fetch(mock_offer, mock_fetch_instance, mock_session)

    mock_fetch_instance.offers.append.assert_called_with(mock_offer_instance)


@patch("src.db.Session")
@patch("src.models.Offer")
def test_link_offer_to_fetch_offer_not_found(mock_offer, mock_session):
    mock_fetch_instance = Mock()
    mock_offer.id = 1
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    with pytest.raises(Exception):  # Adjust this to match the exception you expect
        link_offer_to_fetch(mock_offer, mock_fetch_instance, mock_session)

    mock_fetch_instance.offers.append.assert_not_called()


@patch("src.db.Session")
@patch("src.models.Offer")
def test_link_offer_to_fetch_fetch_not_found(mock_offer, mock_session):
    mock_offer_instance = Mock()
    mock_offer.id = 1
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_offer_instance
    )

    with pytest.raises(Exception):  # Adjust this to match the exception you expect
        link_offer_to_fetch(mock_offer, None, mock_session)

    mock_offer_instance.offers.append.assert_not_called()
