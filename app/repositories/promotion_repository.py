from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from datetime import date
from app.repositories.base_repository import BaseRepository
from app.models.promotion import Promotion
from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate


class PromotionRepository(BaseRepository[Promotion, PromotionCreate, PromotionUpdate]):
    """Repository cho Promotion operations"""
    
    def __init__(self):
        super().__init__(Promotion)
    
    def get_active_promotions(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Promotion]:
        """Get currently active promotions"""
        today = date.today()
        return db.query(Promotion).options(
            joinedload(Promotion.products)
        ).filter(
            and_(
                Promotion.is_active.is_(True),
                Promotion.start_date <= today,
                Promotion.end_date >= today
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_product_id(
        self, 
        db: Session, 
        *, 
        product_id: int
    ) -> List[Promotion]:
        """Get active promotions for a specific product"""
        today = date.today()
        return db.query(Promotion).join(Promotion.products).filter(
            and_(
                Promotion.products.any(id=product_id),
                Promotion.is_active.is_(True),
                Promotion.start_date <= today,
                Promotion.end_date >= today
            )
        ).all()
    
    def get_expired_promotions(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Promotion]:
        """Get expired promotions"""
        today = date.today()
        return db.query(Promotion).filter(
            Promotion.end_date < today
        ).offset(skip).limit(limit).all()
    
    def get_upcoming_promotions(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Promotion]:
        """Get upcoming promotions"""
        today = date.today()
        return db.query(Promotion).filter(
            and_(
                Promotion.start_date > today,
                Promotion.is_active.is_(True)
            )
        ).offset(skip).limit(limit).all()


# Create singleton instance
promotion_repository = PromotionRepository()
