import pytest
from unittest.mock import patch
from psycopg2 import DatabaseError

from src.offers import (
    _fetch_token_from_db,
)
from src.models import JwtToken
from tests.conftest import FUTURE

from sqlalchemy.exc import SQLAlchemyError


@pytest.mark.asyncio
@patch("src.offers.Session")
async def test_success(mocked_session):
    mocked_session.return_value.__enter__.return_value.query.return_value.first.return_value = JwtToken(
        token="test_token", expiration=FUTURE
    )

    result = await _fetch_token_from_db()

    assert isinstance(result, JwtToken)
    assert result.token == "test_token"
    assert result.expiration == FUTURE


@pytest.mark.asyncio
@patch("src.offers.Session")
async def test_failure(mocked_session):
    mocked_session.return_value.__enter__.return_value.query.return_value.first.side_effect = (
        SQLAlchemyError
    )

    with pytest.raises(DatabaseError, match="Database query failed"):
        await _fetch_token_from_db()
