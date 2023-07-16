import pytest
from unittest.mock import patch
from psycopg2 import DatabaseError
from sqlalchemy.exc import SQLAlchemyError

from src.offers import (
    _fetch_token_from_db,
)
from src.models import JwtToken
from tests.conftest import FUTURE


@pytest.mark.asyncio
@patch("src.offers.Session")
async def test_success(mocked_session):
    session_instance = mocked_session.return_value
    session_instance.query.return_value.first.return_value = JwtToken(
        token="test_token", expiration=FUTURE
    )

    result = await _fetch_token_from_db(session=session_instance)

    assert isinstance(result, JwtToken)
    assert result.token == "test_token"
    assert result.expiration == FUTURE


@pytest.mark.asyncio
@patch("src.offers.Session")
async def test_failure(mocked_session):
    session_instance = mocked_session.return_value
    session_instance.query.return_value.first.side_effect = SQLAlchemyError("error")

    with pytest.raises(DatabaseError, match="Database query failed"):
        await _fetch_token_from_db(session=session_instance)
