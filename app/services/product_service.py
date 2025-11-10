from sqlalchemy.orm import Session
from app.database.models import Product, Inventory
from app.schemas.product_schema import ProductCreate, ProductUpdate
from fastapi import HTTPException, status
from typing import List

class ProductService:
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate):
        existing = db.query(Product).filter(Product.code == product_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product code already exists"
            )
        
        product = Product(**product_data.dict())
        db.add(product)
        db.flush()
        
        # Tự động tạo Inventory record
        inventory = Inventory(product_id=product.id)
        db.add(inventory)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def get_all_products(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int):
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    
    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate):
        product = ProductService.get_product_by_id(db, product_id)
        for key, value in product_data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int):
        product = ProductService.get_product_by_id(db, product_id)
        product.is_active = False
        db.commit()
        return {"message": "Product deleted successfully"}