from fastapi import APIRouter, HTTPException, Query
from app.database.db import get_database
from app.schemas.sale import SaleCreate, SaleUpdate
from app.services.sale_service import SaleService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("", response_model=dict)
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    customer_id: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None)
):
    db = get_database()
    service = SaleService(db)
    
    sales = await service.get_all(
        skip=skip, 
        limit=limit, 
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        payment_status=payment_status
    )
    total = await service.get_total_count(
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        payment_status=payment_status
    )
    
    return {
        "sales": sales,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{sale_id}", response_model=dict)
async def get_sale(sale_id: str):
    db = get_database()
    service = SaleService(db)
    sale = await service.get_by_id(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.post("", response_model=dict, status_code=201)
async def create_sale(sale: SaleCreate):
    db = get_database()
    service = SaleService(db)
    # TODO: Lấy user_id từ authentication
    created_by = "user_placeholder"  
    return await service.create(sale, created_by)

@router.put("/{sale_id}", response_model=dict)
async def update_sale(sale_id: str, sale: SaleUpdate):
    db = get_database()
    service = SaleService(db)
    updated = await service.update(sale_id, sale)
    if not updated:
        raise HTTPException(status_code=404, detail="Sale not found")
    return updated

@router.delete("/{sale_id}")
async def delete_sale(sale_id: str):
    db = get_database()
    service = SaleService(db)
    deleted = await service.delete(sale_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Sale deleted successfully"}