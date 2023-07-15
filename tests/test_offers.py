import time
from typing import Optional
import pytest
from unittest.mock import AsyncMock, patch
import httpx
import jwt

import src.env as env
from src.offers import _decode_token, _fetch_new_token_from_api, _is_token_valid
from src.errors import ApiRequestError, InvalidJwtTokenError
from src.models import JwtToken
from tests.conftest import MOCKED_TIME


# _is_token_valid test cases
@pytest.mark.parametrize(
    "token, expected",
    [
        # expired by 1 second
        (JwtToken(token="token1", expiration=(MOCKED_TIME - 1)), False),
        # just expired
        (JwtToken(token="token2", expiration=MOCKED_TIME), False),
        # valid for 1 more second
        (JwtToken(token="token3", expiration=(MOCKED_TIME + 1)), True),
        # Empty token should return False
        (None, False),
    ],
)
def test_is_token_valid(token: Optional[JwtToken], expected: bool):
    assert _is_token_valid(token) == expected


def test_decode_token_invalid_token():
    with pytest.raises(InvalidJwtTokenError):
        _decode_token("invalid_token")


def test_decode_token_gets_decoded():
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
    token = "token123"

    expected_result = {"access_token": token}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mocked_post:
        mocked_post.return_value = AsyncMock(
            json=AsyncMock(return_value=expected_result),
            is_json=True,
            status_code=httpx.codes.OK,
        )

        result = await _fetch_new_token_from_api()

        assert result == token
        mocked_post.assert_called_once_with(
            url=env.API_URL + "/auth",
            headers={"Bearer": env.TOKEN_SECRET},
        )


@pytest.mark.asyncio
async def test_fetch_new_token_from_api_failure():
    error_message = "HTTP request failed"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mocked_post:
        mocked_post.side_effect = httpx.HTTPError(error_message)

        with pytest.raises(ApiRequestError, match=error_message):
            await _fetch_new_token_from_api()


@pytest.mark.asyncio
async def test_fetch_new_token_from_api_valid_response_but_no_token():
    expected_result = {"another_key": "another_value"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mocked_post:
        mocked_post.return_value = AsyncMock(
            json=AsyncMock(return_value=expected_result),
            is_json=True,
            status_code=httpx.codes.OK,
        )

        with pytest.raises(
            ApiRequestError, match="Response does not contain access token"
        ):
            await _fetch_new_token_from_api()


def test_env_vars():
    assert env.TOKEN_SECRET == "mock_token_secret"
