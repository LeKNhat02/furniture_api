from sqlalchemy.orm import Session
from app.database.models import Payment, Sale
from app.schemas.payment_schema import PaymentCreate, PaymentUpdate
from fastapi import HTTPException, status
from typing import List

class PaymentService:
    @staticmethod
    def create_payment(db: Session, payment_data: PaymentCreate) -> Payment:
        # Validate sale exists
        sale = db.query(Sale).filter(Sale.id == payment_data.sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        # Validate amount doesn't exceed sale amount
        total_paid = sum(p.amount for p in sale.payments)
        if total_paid + payment_data.amount > sale.final_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount exceeds sale amount. Remaining: {sale.final_amount - total_paid}"
            )
        
        payment = Payment(**payment_data.dict())
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_all_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
        return db.query(Payment).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment
    
    @staticmethod
    def update_payment(
        db: Session,
        payment_id: int,
        payment_data: PaymentUpdate
    ) -> Payment:
        payment = PaymentService.get_payment_by_id(db, payment_id)
        
        for key, value in payment_data.dict(exclude_unset=True).items():
            setattr(payment, key, value)
        
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def delete_payment(db: Session, payment_id: int):
        payment = PaymentService.get_payment_by_id(db, payment_id)
        db.delete(payment)
        db.commit()