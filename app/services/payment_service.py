from sqlalchemy.orm import Session
from app.database.models import Payment, Sale
from app.schemas.payment_schema import PaymentCreate, PaymentUpdate
from fastapi import HTTPException, status
from typing import List, Optional

class PaymentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Create a new payment"""
        # Validate sale exists
        sale = self.db.query(Sale).filter(Sale.id == payment_data.sale_id).first()
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
        
        payment_dict = payment_data.dict() if hasattr(payment_data, 'dict') else payment_data.__dict__
        payment = Payment(**payment_dict)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_all_payments(self, skip: int = 0, limit: int = 100, search: Optional[str] = None, status: Optional[str] = None, payment_method: Optional[str] = None) -> List[Payment]:
        """Get all payments with pagination, search and filters"""
        query = self.db.query(Payment)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.outerjoin(Sale).filter(
                (Payment.reference_number.ilike(search_term)) |
                (Sale.invoice_number.ilike(search_term))
            )
        
        # Apply status filter
        if status:
            query = query.filter(Payment.status == status)
        
        # Apply payment method filter
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        return query.offset(skip).limit(limit).all()
    
    def get_payments_count(self, search: Optional[str] = None, status: Optional[str] = None, payment_method: Optional[str] = None) -> int:
        """Get total count of payments with optional search and filters"""
        query = self.db.query(Payment)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.outerjoin(Sale).filter(
                (Payment.reference_number.ilike(search_term)) |
                (Sale.invoice_number.ilike(search_term))
            )
        
        # Apply status filter
        if status:
            query = query.filter(Payment.status == status)
        
        # Apply payment method filter
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        return query.count()
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def update_payment(self, payment_id: int, payment_data: PaymentUpdate) -> Payment:
        """Update payment information"""
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        update_dict = payment_data.dict(exclude_unset=True) if hasattr(payment_data, 'dict') else payment_data.__dict__
        for key, value in update_dict.items():
            if value is not None:
                setattr(payment, key, value)
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def delete_payment(self, payment_id: int):
        """Delete payment"""
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        self.db.delete(payment)
        self.db.commit()
        return {"message": "Payment deleted successfully"}