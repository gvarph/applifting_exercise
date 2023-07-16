from unittest.mock import create_autospec, patch
from sqlalchemy.orm import Session
import pytest

from src.db import session_scope


def test_session_scope():
    mock_session = create_autospec(Session, instance=True)

    with patch("src.db.SessionMkr", return_value=mock_session) as mock_Session:
        with session_scope() as session:
            assert session is mock_session

        # Verify the methods were called correctly
        mock_Session.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

        # Verify that rollback was not called (as no exception was raised)
        mock_session.rollback.assert_not_called()


def test_session_scope_with_exception():
    mock_session = create_autospec(Session, instance=True)

    with patch("src.db.SessionMkr", return_value=mock_session) as mock_Session:
        with pytest.raises(Exception):
            with session_scope() as session:
                assert session is mock_session
                raise Exception("Test exception")

        # Verify the methods were called correctly
        mock_Session.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

        # Verify that commit was not called (as an exception was raised)
        mock_session.commit.assert_not_called()
