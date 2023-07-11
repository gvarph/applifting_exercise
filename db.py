from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import consts


engine = create_engine(
    engine=create_engine(
        f"postgresql://{consts.postgres_user}:{consts.postgres_password}@{consts.postgres_host}:{consts.postgres_port}/{consts.postgres_db}"
    ),
)


Session = sessionmaker(bind=engine)
