from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.payment import Payment
from app.schemas.payment_schema import PaymentCreate, PaymentUpdate


class PaymentRepository(BaseRepository[Payment, PaymentCreate, PaymentUpdate]):
    """Repository cho Payment operations"""
    
    def __init__(self):
        super().__init__(Payment)
    
    def get_by_sale_id(self, db: Session, *, sale_id: int) -> List[Payment]:
        """Get payments for a specific sale"""
        return db.query(Payment).filter(Payment.sale_id == sale_id).all()
    
    def get_by_method(
        self, 
        db: Session, 
        *, 
        payment_method: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payment]:
        """Get payments by method"""
        return db.query(Payment).filter(
            Payment.payment_method == payment_method
        ).offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        db: Session, 
        *, 
        status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payment]:
        """Get payments by status"""
        return db.query(Payment).filter(
            Payment.status == status
        ).offset(skip).limit(limit).all()


# Create singleton instance
payment_repository = PaymentRepository()
