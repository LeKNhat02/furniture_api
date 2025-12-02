from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import Sale, Customer
from app.schemas.payment_schema import (
    PaymentCreate, PaymentUpdate, PaymentResponse
)
from app.services.payment_service import PaymentService
from app.core.security import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Payments"])

def _enrich_payment_with_customer_info(db: Session, payment):
    """Helper function to add customer info to payment response"""
    sale = db.query(Sale).filter(Sale.id == payment.sale_id).first()
    customer = None
    if sale:
        customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
    
    payment_dict = {
        "id": payment.id,
        "sale_id": payment.sale_id,
        "payment_method": payment.payment_method,
        "amount": payment.amount,
        "reference_number": payment.reference_number,
        "notes": payment.notes,
        "payment_date": payment.payment_date,
        "status": payment.status,
        "created_at": payment.created_at,
        # Customer info from Sale
        "customer_id": sale.customer_id if sale else None,
        "customer_name": customer.name if customer else None,
        "customer_phone": customer.phone if customer else None,
        "sale_name": sale.invoice_number if sale else None,
    }
    return payment_dict

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record a new payment"""
    try:
        service = PaymentService(db)
        payment = service.create_payment(payment_data)
        
        # Enrich with customer info
        enriched = _enrich_payment_with_customer_info(db, payment)
        
        return {
            "data": enriched,
            "message": "Payment created successfully",
            "status_code": 201
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_payments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search by reference number or sale invoice"),
    status: str = Query(None, description="Filter by payment status"),
    payment_method: str = Query(None, description="Filter by payment method"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all payments with pagination, search and filters"""
    try:
        skip = (page - 1) * limit
        service = PaymentService(db)
        payments = service.get_all_payments(skip, limit, search=search, status=status, payment_method=payment_method)
        total_count = service.get_payments_count(search=search, status=status, payment_method=payment_method)
        
        # Enrich all payments with customer info
        enriched_payments = [_enrich_payment_with_customer_info(db, p) for p in payments]
        
        return {
            "data": enriched_payments,
            "message": "Payments retrieved successfully",
            "status_code": 200,
            "page": page,
            "limit": limit,
            "total": total_count
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{payment_id}")
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get payment by ID"""
    try:
        service = PaymentService(db)
        payment = service.get_payment_by_id(payment_id)
        
        # Enrich with customer info
        enriched = _enrich_payment_with_customer_info(db, payment)
        
        return {
            "data": enriched,
            "message": "Payment retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment {payment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{payment_id}")
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update payment status"""
    try:
        service = PaymentService(db)
        payment = service.update_payment(payment_id, payment_data)
        
        # Enrich with customer info
        enriched = _enrich_payment_with_customer_info(db, payment)
        
        return {
            "data": enriched,
            "message": "Payment updated successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error updating payment {payment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete payment"""
    try:
        service = PaymentService(db)
        service.delete_payment(payment_id)
        return {
            "data": None,
            "message": "Payment deleted successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error deleting payment {payment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))