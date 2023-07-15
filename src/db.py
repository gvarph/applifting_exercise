from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import src.env as env


engine = create_engine(
    env.DATABASE_URL,
)


Session = sessionmaker(bind=engine)
