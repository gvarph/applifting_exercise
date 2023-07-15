from typing import Optional
import pytest
import jwt


from src.offers import (
    _decode_token,
    _is_token_valid,
)
from src.errors import InvalidJwtTokenError
from src.models import JwtToken
from tests.conftest import PAST, PRESENT, FUTURE


# _is_token_valid test cases
@pytest.mark.parametrize(
    "token, expected",
    [
        # expired by 1 second
        (JwtToken(token="token1", expiration=PAST), False),
        # just expired
        (JwtToken(token="token2", expiration=PRESENT), False),
        # valid for 1 more second
        (JwtToken(token="token3", expiration=FUTURE), True),
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
