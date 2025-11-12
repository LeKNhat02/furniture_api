from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.models import Promotion, Product
from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate, PromotionResponse
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

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
            min_purchase=promotion_data.min_purchase,  # Add new fields
            max_discount=promotion_data.max_discount,   # Add new fields
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
    def get_all_promotions(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[PromotionResponse]:
        """Get promotions and transform to frontend format"""
        query = db.query(Promotion)
        
        if search:
            query = query.filter(
                or_(
                    Promotion.name.contains(search),
                    Promotion.description.contains(search)
                )
            )
        
        if is_active is not None:
            query = query.filter(Promotion.is_active == is_active)
        
        promotions = query.offset(skip).limit(limit).all()
        
        # Transform to frontend format
        return [
            PromotionService._transform_promotion_response(promotion)
            for promotion in promotions
        ]
    
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
    def get_active_promotions(db: Session) -> List[PromotionResponse]:
        """Get active promotions in frontend format"""
        promotions = db.query(Promotion).filter(Promotion.is_active).all()
        return [
            PromotionService._transform_promotion_response(promotion)
            for promotion in promotions
        ]
    
    @staticmethod
    def _transform_promotion_response(promotion: Promotion) -> PromotionResponse:
        """Transform database model to frontend-compatible response"""
        # Normalize discount_type to frontend format
        discount_type_mapping = {
            "PERCENTAGE": "percentage",
            "percentage": "percentage",
            "FIXED": "fixed_amount",
            "fixed_amount": "fixed_amount"
        }
        
        return PromotionResponse(
            id=str(promotion.id),  # Convert to String
            name=promotion.name,
            description=promotion.description,
            discountType=discount_type_mapping.get(promotion.discount_type, "percentage"),  # camelCase + normalize
            discountValue=promotion.discount_value,  # camelCase
            minPurchase=promotion.min_purchase,  # camelCase
            maxDiscount=promotion.max_discount,  # camelCase
            startDate=datetime.combine(promotion.start_date, datetime.min.time()),  # camelCase + convert to datetime
            endDate=datetime.combine(promotion.end_date, datetime.min.time()),    # camelCase + convert to datetime
            isActive=promotion.is_active,  # camelCase
            createdAt=promotion.created_at,  # camelCase
            updatedAt=promotion.updated_at   # camelCase
        )