from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.sale_schema import (
    SaleCreate, SaleUpdate, SaleResponse
)
from app.services.sale_service import SaleService
from app.core.security import get_current_user
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/sales", tags=["Sales"])

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new sale"""
    return SaleService.create_sale(db, sale_data, current_user.id)

@router.get("/", response_model=List[SaleResponse])
def get_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all sales with filters"""
    skip = (page - 1) * limit
    return SaleService.get_all_sales(
        db, skip, limit, search, status, start_date, end_date
    )

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sale by ID"""
    return SaleService.get_sale_by_id(db, sale_id)

@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale_data: SaleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update sale status or notes"""
    return SaleService.update_sale(db, sale_id, sale_data)

@router.patch("/{sale_id}/cancel", response_model=SaleResponse)
def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel sale and restore inventory"""
    return SaleService.cancel_sale(db, sale_id)

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete sale and restore inventory"""
    SaleService.delete_sale(db, sale_id)
    return None