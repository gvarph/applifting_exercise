from typing import Optional
import pytest
from unittest.mock import AsyncMock, patch
import time
import httpx
import jwt

from src.errors import InvalidJwtTokenError
from src.models import JwtToken

MOCKED_TIME = 1599999999.9


# this is required to make time.time() in tests consistent
@pytest.fixture(autouse=True)
def mock_time(monkeypatch):
    class mytime:
        @classmethod
        def time(cls):
            return MOCKED_TIME

    monkeypatch.setattr(time, "time", mytime.time)


# _is_token_valid test cases
@pytest.mark.parametrize(
    "token, expected",
    [
        (JwtToken(token="token1", expiration=(MOCKED_TIME - 10)), False),
        (JwtToken(token="token2", expiration=MOCKED_TIME), False),
        (JwtToken(token="token3", expiration=(MOCKED_TIME + 100)), True),
        (None, False),  # Empty token should return False
    ],
)
def test_is_token_valid(token: Optional[JwtToken], expected: bool):
    from src.offers import _is_token_valid

    assert _is_token_valid(token) == expected


def test_decode_token_invalid_token():
    from src.offers import _decode_token

    with pytest.raises(InvalidJwtTokenError):
        _decode_token("invalid_token")


def test_decode_token_gets_decoded():
    from src.offers import _decode_token

    sample_headers = {"alg": "HS256", "typ": "JWT"}

    sample_payload = {
        "token": "f276da53-f937-477e-a4a1-8e9968cb4f23",
        "expires": 1499999999,
    }

    sample = jwt.encode(
        sample_payload, "secret", algorithm="HS256", headers=sample_headers
    )

    decoded = _decode_token(sample)

    assert decoded == sample_payload


@pytest.mark.asyncio
async def test_fetch_new_token_from_api_success():
    from src.offers import _fetch_new_token_from_api
    from src.env import API_URL, TOKEN_SECRET

    token = "token123"

    expected_result = {"access_token": token}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mocked_post:
        mocked_post.return_value = AsyncMock(
            json=AsyncMock(return_value=expected_result),
            is_json=True,
            status_code=200,
        )

        result = await _fetch_new_token_from_api()

        assert result == token
        mocked_post.assert_called_once_with(
            url=API_URL + "/auth",
            headers={"Bearer": TOKEN_SECRET},
        )


@pytest.mark.asyncio
async def test_fetch_new_token_from_api_failure():
    from src.offers import _fetch_new_token_from_api, ApiRequestError

    error_message = "HTTP request failed"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mocked_post:
        mocked_post.side_effect = httpx.HTTPError(error_message)

        with pytest.raises(ApiRequestError, match=error_message):
            await _fetch_new_token_from_api()


@pytest.mark.asyncio
async def test_fetch_new_token_from_api_valid_response_but_no_token():
    from src.offers import _fetch_new_token_from_api, ApiRequestError

    expected_result = {"another_key": "another_value"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mocked_post:
        mocked_post.return_value = AsyncMock(
            json=AsyncMock(return_value=expected_result),
            is_json=True,
            status_code=200,
        )

        with pytest.raises(
            ApiRequestError, match="Response does not contain access token"
        ):
            await _fetch_new_token_from_api()
