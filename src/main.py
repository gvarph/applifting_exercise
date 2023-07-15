from uuid import uuid4
import uuid

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder

from src.db import Session
from models import Product, ProductModel

app = FastAPI()


@app.get("/products/", response_model=list[ProductModel], status_code=200)
async def read_products():
    try:
        with Session() as session:
            all_products = session.query(Product).all()

        # convert to ProductModel
        models = [
            ProductModel(
                id=product.id, name=product.name, description=product.description
            )
            for product in all_products
        ]
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/products/", response_model=ProductModel, status_code=201)
def create_product(data: ProductModel):
    if not data.name or not data.description:
        raise HTTPException(status_code=400, detail="Invalid product")
    try:
        with Session() as session:
            db_product = data.toProduct()
            session.add(db_product)
            session.commit()
            session.refresh(db_product)

        # TODO: register product in offers service?

        return db_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/products/{product_id}", status_code=200)
async def update_product(product_id: uuid.UUID, new_product: ProductModel):
    try:
        with Session() as session:
            session.query(Product).filter(Product.id == product_id).update(
                {
                    Product.name: new_product.name,
                    Product.description: new_product.description,
                }
            )
            session.commit()

            # TODO: update product in offers service?
            db_product = session.query(Product).filter(Product.id == product_id).first()
        print(db_product)
        return db_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: uuid.UUID):
    try:
        with Session() as session:
            delete_stmt = (
                session.query(Product).filter(Product.id == product_id).delete()
            )

            if not delete_stmt:
                raise HTTPException(status_code=404, detail="Product not found")
            session.commit()
            # TODO: delete product in offers service?
        return status.HTTP_204_NO_CONTENT

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
