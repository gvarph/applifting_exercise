import os
from dotenv import load_dotenv

load_dotenv(".env")

postgres_db = os.getenv("POSTGRES_DB")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")

refresh_token_secret = os.getenv("REFRESH_TOKEN_SECRET")
