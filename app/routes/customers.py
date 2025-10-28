from fastapi import APIRouter, Depends, HTTPException, Query
from app.database.db import get_database
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.customer_service import CustomerService
from typing import Optional

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("", response_model=dict)
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    db = get_database()
    service = CustomerService(db)
    
    customers = await service.get_all(skip=skip, limit=limit, search=search)
    total = await service.get_total_count(search=search)
    
    return {
        "customers": customers,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{customer_id}", response_model=dict)
async def get_customer(customer_id: str):
    db = get_database()
    service = CustomerService(db)
    customer = await service.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("", response_model=dict, status_code=201)
async def create_customer(customer: CustomerCreate):
    db = get_database()
    service = CustomerService(db)
    return await service.create(customer)

@router.put("/{customer_id}", response_model=dict)
async def update_customer(customer_id: str, customer: CustomerUpdate):
    db = get_database()
    service = CustomerService(db)
    updated = await service.update(customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated

@router.delete("/{customer_id}")
async def delete_customer(customer_id: str):
    db = get_database()
    service = CustomerService(db)
    deleted = await service.delete(customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}