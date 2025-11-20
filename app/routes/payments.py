from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.payment_schema import (
    PaymentCreate, PaymentUpdate, PaymentResponse
)
from app.services.payment_service import PaymentService
from app.core.security import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Payments"])

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
        return {
            "data": payment,
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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all payments"""
    try:
        service = PaymentService(db)
        payments = service.get_all_payments(skip, limit)
        return {
            "data": payments,
            "message": "Payments retrieved successfully",
            "status_code": 200
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
        return {
            "data": payment,
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
        return {
            "data": payment,
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