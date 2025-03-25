from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Product
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProductCreate(BaseModel):
    name:str
    description:str
    price:float

@router.post("/products/")
def create_product(product:ProductCreate, db:Session = Depends(get_db)):
    db_product = Product(name=product.name, description=product.description, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products/")
def read_products(db:Session=Depends(get_db)):
    return db.query(Product).all()

@router.get("/products/{product_id}")
def read_product(product_id:int, db:Session=Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found!")
    return product

@router.put("/products/{product_id}")
def update_product(product_id:int, product:ProductCreate, db:Session=Depends(get_db)):
    db_product = db.query(Product).filter(Product.id==product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id:int, db:Session=Depends(get_db)):
    db_product = db.query(Product).filter(Product.id==product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message":"Product Deleted successfully"}
