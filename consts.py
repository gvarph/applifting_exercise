import os
from dotenv import load_dotenv

load_dotenv(".env")

postgres_db = os.getenv("POSTGRES_DB")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")

DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

token_secret = os.getenv("REFRESH_TOKEN_SECRET")

base_url = "https://python.exercise.applifting.cz/api/v1"
