from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.sale_schema import (
    SaleCreate, SaleUpdate, SaleResponse
)
from app.services.sale_service import SaleService
from app.core.security import get_current_user
from typing import List

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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all sales"""
    return SaleService.get_all_sales(db, skip, limit)

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

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete (cancel) sale and restore inventory"""
    SaleService.delete_sale(db, sale_id)
    return None