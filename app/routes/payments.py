from fastapi import APIRouter, HTTPException, Query
from app.database.db import get_database
from app.schemas.payment import PaymentCreate
from app.services.payment_service import PaymentService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("", response_model=dict)
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sale_id: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    db = get_database()
    service = PaymentService(db)
    
    payments = await service.get_all(
        skip=skip, 
        limit=limit, 
        sale_id=sale_id,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date
    )
    total = await service.get_total_count(
        sale_id=sale_id,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "payments": payments,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/by-sale/{sale_id}", response_model=list)
async def get_payments_by_sale(sale_id: str):
    """Lấy tất cả payments của một sale"""
    db = get_database()
    service = PaymentService(db)
    return await service.get_by_sale_id(sale_id)

@router.get("/{payment_id}", response_model=dict)
async def get_payment(payment_id: str):
    db = get_database()
    service = PaymentService(db)
    payment = await service.get_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("", response_model=dict, status_code=201)
async def create_payment(payment: PaymentCreate):
    db = get_database()
    service = PaymentService(db)
    # TODO: Lấy user_id từ authentication
    created_by = "user_placeholder"
    return await service.create(payment, created_by)

@router.delete("/{payment_id}")
async def delete_payment(payment_id: str):
    db = get_database()
    service = PaymentService(db)
    deleted = await service.delete(payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}