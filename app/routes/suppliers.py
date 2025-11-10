from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.supplier_schema import (
    SupplierCreate, SupplierUpdate, SupplierResponse
)
from app.services.supplier_service import SupplierService
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new supplier"""
    return SupplierService.create_supplier(db, supplier_data)

@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query("", max_length=255),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all suppliers with search"""
    return SupplierService.get_all_suppliers(db, skip, limit, search)

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get supplier by ID"""
    return SupplierService.get_supplier_by_id(db, supplier_id)

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update supplier"""
    return SupplierService.update_supplier(db, supplier_id, supplier_data)

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete supplier"""
    SupplierService.delete_supplier(db, supplier_id)
    return None