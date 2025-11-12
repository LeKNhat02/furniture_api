from sqlalchemy.orm import Session
from app.repositories import product_repository
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List
import os
import uuid

class ProductService:
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> ProductResponse:
        """Create new product using repository"""
        return product_repository.create_with_inventory(db=db, obj_in=product_data)
    
    @staticmethod
    def get_all_products(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[ProductResponse]:
        """Get products with frontend-compatible transformation"""
        return product_repository.search_products(
            db=db, 
            skip=skip, 
            limit=limit, 
            search=search
        )
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> ProductResponse:
        """Get single product with frontend-compatible transformation"""
        product = product_repository.get_with_inventory(db=db, id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    
    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> ProductResponse:
        """Update product using repository"""
        updated_product = product_repository.update(db=db, db_obj_id=product_id, obj_in=product_data)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return updated_product
    
    @staticmethod
    def delete_product(db: Session, product_id: int):
        """Soft delete product using repository"""
        success = product_repository.remove(db=db, id=product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return {"message": "Product deleted successfully"}
    
    @staticmethod
    def get_low_stock_products(db: Session, limit: int = 50) -> List[ProductResponse]:
        """Get products with low stock using repository"""
        return product_repository.get_low_stock_products(db=db, limit=limit)
    
    @staticmethod
    def save_product_image(image: UploadFile, product_id: int) -> str:
        """Save product image and return URL"""
        # Tạo thư mục uploads nếu chưa có
        upload_dir = "uploads/products"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Tạo tên file unique
        file_ext = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
        filename = f"{product_id}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        # Lưu file
        with open(file_path, "wb") as buffer:
            content = image.file.read()
            buffer.write(content)
        
        # Trả về URL (relative path)
        return f"/uploads/products/{filename}"
    
    @staticmethod
    def search_by_category(
        db: Session, 
        category: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ProductResponse]:
        """Search products by category using repository"""
        return product_repository.search_products(
            db=db,
            search=category,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    def get_product_statistics(db: Session) -> dict:
        """Get product statistics"""
        total_products = product_repository.count_all(db=db)
        low_stock_count = len(product_repository.get_low_stock_products(db=db, limit=1000))
        
        return {
            "total_products": total_products,
            "low_stock_products": low_stock_count,
            "active_products": total_products  # Assuming all retrieved are active
        }