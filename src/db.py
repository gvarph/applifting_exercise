from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .util import get_logger
from .env import DATABASE_URL

logger = get_logger(__name__)

engine = create_engine(
    DATABASE_URL,
)

SessionMkr = sessionmaker(bind=engine)


@contextmanager
def session_scope() -> Generator[Session, Any, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionMkr()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
