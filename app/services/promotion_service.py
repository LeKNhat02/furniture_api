from sqlalchemy.orm import Session
from app.database.models import Promotion, Product
from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate
from fastapi import HTTPException, status
from datetime import date
from typing import List, Optional

class PromotionService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_promotion(self, promotion_data: PromotionCreate) -> Promotion:
        """Create a new promotion"""
        # Validate dates
        if promotion_data.start_date >= promotion_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        promotion = Promotion(
            name=promotion_data.name,
            description=promotion_data.description,
            discount_type=promotion_data.discount_type,
            discount_value=promotion_data.discount_value,
            start_date=promotion_data.start_date,
            end_date=promotion_data.end_date,
            is_active=promotion_data.is_active
        )
        
        self.db.add(promotion)
        self.db.flush()
        
        # Add products if provided
        if promotion_data.product_ids:
            for product_id in promotion_data.product_ids:
                product = self.db.query(Product).filter(Product.id == product_id).first()
                if product:
                    promotion.products.append(product)
        
        self.db.commit()
        self.db.refresh(promotion)
        return promotion
    
    def get_all_promotions(self, skip: int = 0, limit: int = 100) -> List[Promotion]:
        """Get all promotions with pagination"""
        return self.db.query(Promotion).offset(skip).limit(limit).all()
    
    def get_promotion_by_id(self, promotion_id: int) -> Optional[Promotion]:
        """Get promotion by ID"""
        return self.db.query(Promotion).filter(Promotion.id == promotion_id).first()
    
    def update_promotion(self, promotion_id: int, promotion_data: PromotionUpdate) -> Promotion:
        """Update promotion information"""
        promotion = self.get_promotion_by_id(promotion_id)
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found"
            )
        
        # Validate dates
        if promotion_data.start_date >= promotion_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        update_dict = promotion_data.dict(exclude_unset=True) if hasattr(promotion_data, 'dict') else promotion_data.__dict__
        for key, value in update_dict.items():
            if key != "product_ids" and value is not None:
                setattr(promotion, key, value)
        
        # Update products if provided
        if hasattr(promotion_data, 'product_ids') and promotion_data.product_ids is not None:
            promotion.products.clear()
            for product_id in promotion_data.product_ids:
                product = self.db.query(Product).filter(Product.id == product_id).first()
                if product:
                    promotion.products.append(product)
        
        self.db.commit()
        self.db.refresh(promotion)
        return promotion
    
    def delete_promotion(self, promotion_id: int):
        """Delete promotion"""
        promotion = self.get_promotion_by_id(promotion_id)
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found"
            )
        self.db.delete(promotion)
        self.db.commit()
        return {"message": "Promotion deleted successfully"}
    
    def get_active_promotions(self) -> List[Promotion]:
        """Get active promotions"""
        return self.db.query(Promotion).filter(Promotion.is_active == True).all()