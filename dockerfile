from python:3.10

# Set the working directory to /app
WORKDIR /app

# Copy and install dependencies
copy pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main

# copy the project code into the container
COPY ./src /app/src


EXPOSE 8000

# Run the app when the container launches
CMD ["poetry", "run", "uvicorn", "src.main:app" ,"--host", "0.0.0.0", "--port", "8000"]



