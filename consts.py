import os
from dotenv import load_dotenv

load_dotenv(".env")

# Now you can access the variables
postgres_db = os.getenv("POSTGRES_DB")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
