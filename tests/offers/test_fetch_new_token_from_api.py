import pytest
from unittest.mock import AsyncMock, patch
import httpx
import src.env as env
from src.offers import _fetch_new_token_from_api
from src.errors import ApiRequestError


@pytest.mark.asyncio
async def test_success():
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
async def test_failure():
    error_message = "HTTP request failed"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mocked_post:
        mocked_post.side_effect = httpx.HTTPError(error_message)

        with pytest.raises(ApiRequestError, match=error_message):
            await _fetch_new_token_from_api()


@pytest.mark.asyncio
async def test_valid_response_but_no_token():
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
