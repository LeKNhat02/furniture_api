from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.customer_schema import (
    CustomerCreate, CustomerUpdate, CustomerResponse
)
from app.services.customer_service import CustomerService
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new customer"""
    return CustomerService.create_customer(db, customer_data)

@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query("", max_length=255),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all customers with search"""
    return CustomerService.get_all_customers(db, skip, limit, search)

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get customer by ID"""
    return CustomerService.get_customer_by_id(db, customer_id)

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update customer"""
    return CustomerService.update_customer(db, customer_id, customer_data)

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete customer"""
    CustomerService.delete_customer(db, customer_id)
    return None

