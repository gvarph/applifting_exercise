from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from .env import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
)


Session = sessionmaker(bind=engine)
