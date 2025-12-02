from sqlalchemy.orm import Session
from app.database.models import Product, Inventory
from app.schemas.product_schema import ProductCreate, ProductUpdate
from fastapi import HTTPException, status
from typing import List, Optional

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, product_data: ProductCreate):
        existing = self.db.query(Product).filter(Product.code == product_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product code already exists"
            )
        
        product_dict = product_data.dict() if hasattr(product_data, 'dict') else product_data.__dict__
        product = Product(**product_dict)
        self.db.add(product)
        self.db.flush()
        
        # Tự động tạo Inventory record
        inventory = Inventory(product_id=product.id)
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_all_products(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Product]:
        query = self.db.query(Product).filter(Product.is_active)
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_term)) | 
                (Product.code.ilike(search_term)) |
                (Product.category.ilike(search_term))
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_products_count(self, search: Optional[str] = None) -> int:
        """Get total count of products with optional search filter"""
        query = self.db.query(Product).filter(Product.is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_term)) | 
                (Product.code.ilike(search_term)) |
                (Product.category.ilike(search_term))
            )
        
        return query.count()
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def update_product(self, product_id: int, product_data: ProductUpdate):
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        update_dict = product_data.dict(exclude_unset=True) if hasattr(product_data, 'dict') else product_data.__dict__
        for key, value in update_dict.items():
            if value is not None:
                setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int):
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        product.is_active = False
        self.db.commit()
        return {"message": "Product deleted successfully"}
    
    # Static methods for backward compatibility with old routes
    @staticmethod
    def create_product_static(db: Session, product_data: ProductCreate):
        service = ProductService(db)
        return service.create_product(product_data)
    
    @staticmethod
    def get_all_products_static(db: Session, skip: int = 0, limit: int = 100):
        service = ProductService(db)
        return service.get_all_products(skip, limit)
    
    @staticmethod
    def get_product_by_id_static(db: Session, product_id: int):
        service = ProductService(db)
        return service.get_product_by_id(product_id)
    
    @staticmethod
    def update_product_static(db: Session, product_id: int, product_data):
        service = ProductService(db)
        return service.update_product(product_id, product_data)
    
    @staticmethod
    def delete_product_static(db: Session, product_id: int):
        service = ProductService(db)
        return service.delete_product(product_id)