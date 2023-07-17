import time

import pytest

MOCKED_TIME = 1599999999.9
PAST = MOCKED_TIME - 1
PRESENT = MOCKED_TIME
FUTURE = MOCKED_TIME + 1


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
