from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/products/")
def read_products():
    raise NotImplementedError  # TODO


@app.post("/products/")
def create_product():
    raise NotImplementedError  # TODO


@app.put("/products/{product_id}")
def update_product(product_id: int):
    raise NotImplementedError  # TODO


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    raise NotImplementedError  # TODO
