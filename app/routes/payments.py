from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.payment_schema import (
    PaymentCreate, PaymentUpdate, PaymentResponse
)
from app.services.payment_service import PaymentService
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record a new payment"""
    return PaymentService.create_payment(db, payment_data)

@router.get("/", response_model=List[PaymentResponse])
def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all payments"""
    return PaymentService.get_all_payments(db, skip, limit)

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get payment by ID"""
    return PaymentService.get_payment_by_id(db, payment_id)

@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update payment status"""
    return PaymentService.update_payment(db, payment_id, payment_data)

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete payment"""
    PaymentService.delete_payment(db, payment_id)
    return None