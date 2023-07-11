
# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Use POSTGRES_PASSWORD from environment variable
docker run --name dev-postgres -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -p 5432:5432 -d postgres