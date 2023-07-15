from importlib import reload
import os
import time
from unittest.mock import patch
import pytest

MOCKED_TIME = 1599999999.9


# this is required to make time.time() in tests consistent.
# Otherwise, it will be different in every test run and that can cause
# some tests to fail
@pytest.fixture(autouse=True)
def mock_time(monkeypatch):
    class mytime:
        @classmethod
        def time(cls):
            return MOCKED_TIME

    monkeypatch.setattr(time, "time", mytime.time)


@pytest.fixture(autouse=True)
def mock_config():
    with patch("src.env.DATABASE_URL", "mock_database_url"), patch(
        "src.env.TOKEN_SECRET", "mock_token_secret"
    ), patch("src.env.API_URL", "mock_api_url"), patch(
        "src.env.LOG_LEVEL", "mock_log_level"
    ):
        yield
