from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.inventory_schema import (
    InventoryResponse, InventoryTransactionCreate, InventoryTransactionResponse
)
from app.services.inventory_service import InventoryService
from app.core.security import get_current_user
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

@router.get("/", response_model=List[InventoryResponse])
def get_inventory_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all inventory"""
    return InventoryService.get_inventory_list(db, skip, limit)

@router.get("/product/{product_id}", response_model=InventoryResponse)
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory for a specific product"""
    return InventoryService.get_inventory_by_product(db, product_id)

@router.post("/transaction", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def add_inventory_transaction(
    transaction: InventoryTransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add inventory transaction (IN, OUT, ADJUSTMENT)"""
    return InventoryService.add_transaction(db, transaction)

@router.get("/transactions", response_model=List[InventoryTransactionResponse])
def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    product_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory transactions with filters"""
    skip = (page - 1) * limit
    return InventoryService.get_transactions(
        db, skip, limit, product_id, type, start_date, end_date
    )

@router.get("/low-stock/list", response_model=List[InventoryResponse])
def get_low_stock(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get products with low stock"""
    return InventoryService.get_low_stock_products(db)