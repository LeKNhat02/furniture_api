from sqlalchemy.orm import Session
from app.database.models import Promotion, Product
from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate
from fastapi import HTTPException, status
from datetime import date
from typing import List

class PromotionService:
    @staticmethod
    def create_promotion(db: Session, promotion_data: PromotionCreate) -> Promotion:
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
        
        db.add(promotion)
        db.flush()
        
        # Add products if provided
        if promotion_data.product_ids:
            for product_id in promotion_data.product_ids:
                product = db.query(Product).filter(Product.id == product_id).first()
                if product:
                    promotion.products.append(product)
        
        db.commit()
        db.refresh(promotion)
        return promotion
    
    @staticmethod
    def get_all_promotions(db: Session, skip: int = 0, limit: int = 100) -> List[Promotion]:
        return db.query(Promotion).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_promotion_by_id(db: Session, promotion_id: int) -> Promotion:
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found"
            )
        return promotion
    
    @staticmethod
    def update_promotion(
        db: Session,
        promotion_id: int,
        promotion_data: PromotionUpdate
    ) -> Promotion:
        promotion = PromotionService.get_promotion_by_id(db, promotion_id)
        
        # Validate dates
        if promotion_data.start_date >= promotion_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        for key, value in promotion_data.dict(exclude_unset=True).items():
            if key != "product_ids":
                setattr(promotion, key, value)
        
        # Update products if provided
        if promotion_data.product_ids is not None:
            promotion.products.clear()
            for product_id in promotion_data.product_ids:
                product = db.query(Product).filter(Product.id == product_id).first()
                if product:
                    promotion.products.append(product)
        
        db.commit()
        db.refresh(promotion)
        return promotion
    
    @staticmethod
    def delete_promotion(db: Session, promotion_id: int):
        promotion = PromotionService.get_promotion_by_id(db, promotion_id)
        db.delete(promotion)
        db.commit()
    
    @staticmethod
    def get_active_promotions(db: Session) -> List[Promotion]:
        return db.query(Promotion).filter(Promotion.is_active == True).all()