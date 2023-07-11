from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import consts


engine = create_engine(
    consts.DATABASE_URL,
)


Session = sessionmaker(bind=engine)
