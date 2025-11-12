from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.models import Payment, Sale, Customer
from app.schemas.payment_schema import PaymentCreate, PaymentUpdate, PaymentResponse
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

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
    def get_all_payments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        payment_method: Optional[str] = None,
        sale_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PaymentResponse]:
        """Get payments with filters and transform to frontend format"""
        query = (
            db.query(
                Payment,
                Sale.invoice_number.label("sale_name"),
                Sale.customer_id.label("customer_id_ref"),
                Customer.name.label("customer_name")
            )
            .join(Sale, Payment.sale_id == Sale.id)
            .join(Customer, Sale.customer_id == Customer.id)
        )
        
        if search:
            query = query.filter(
                or_(
                    Payment.reference_number.contains(search),
                    Customer.name.contains(search),
                    Customer.phone.contains(search)
                )
            )
        
        if status_filter:
            query = query.filter(Payment.status == status_filter)
        
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        if sale_id:
            query = query.filter(Payment.sale_id == sale_id)
        
        if customer_id:
            query = query.filter(Sale.customer_id == customer_id)
        
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        results = query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()
        
        # Transform to frontend format
        return [
            PaymentService._transform_payment_response(payment, sale_name, customer_name, customer_id_ref)
            for payment, sale_name, customer_id_ref, customer_name in results
        ]
    
    @staticmethod
    def refund_payment(db: Session, payment_id: int, notes: Optional[str] = None) -> Payment:
        """Refund a payment"""
        payment = PaymentService.get_payment_by_id(db, payment_id)
        
        if payment.status == "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot refund a failed payment"
            )
        
        # Create refund payment (negative amount)
        refund = Payment(
            sale_id=payment.sale_id,
            payment_method=payment.payment_method,
            amount=-payment.amount,
            payment_date=datetime.now(),
            status="completed",
            reference_number=f"REFUND-{payment.reference_number or payment.id}",
            notes=notes or f"Refund for payment {payment.id}"
        )
        
        payment.status = "failed"
        db.add(refund)
        db.commit()
        db.refresh(refund)
        return refund
    
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
    
    @staticmethod
    def _transform_payment_response(
        payment: Payment,
        sale_name: str = "",
        customer_name: str = "",
        customer_id: int = None
    ) -> PaymentResponse:
        """Transform database model to frontend-compatible response"""
        # Normalize payment method to frontend format
        method_mapping = {
            "CASH": "cash",
            "cash": "cash",
            "CARD": "transfer",  # Map card to transfer for frontend
            "BANK_TRANSFER": "transfer",
            "transfer": "transfer",
            "OTHER": "cash"  # Default unknown to cash
        }
        
        return PaymentResponse(
            id=str(payment.id),  # Convert to String
            saleId=str(payment.sale_id),  # camelCase + String
            saleName=sale_name or "",  # Include sale reference
            customerId=str(customer_id) if customer_id else "",  # camelCase + String
            customerName=customer_name or "",  # Include customer name
            amount=payment.amount,
            paymentMethod=method_mapping.get(payment.payment_method, "cash"),  # camelCase + normalize
            status=payment.status,
            paymentDate=payment.payment_date,  # camelCase
            transactionId=payment.reference_number,  # Map reference_number to transactionId
            bankName=None,  # Will be added when bank info is stored
            accountNumber=None,  # Will be added when bank info is stored
            notes=payment.notes,
            createdAt=payment.payment_date,  # camelCase, use payment_date as createdAt
            updatedAt=None  # Will be added when updated_at field is available
        )