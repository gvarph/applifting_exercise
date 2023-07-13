from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import env


engine = create_engine(
    env.DATABASE_URL,
)


Session = sessionmaker(bind=engine)
