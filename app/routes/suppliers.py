from fastapi import APIRouter, HTTPException, Query
from app.database.db import get_database
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.services.supplier_service import SupplierService
from typing import Optional

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.get("", response_model=dict)
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    db = get_database()
    service = SupplierService(db)
    
    suppliers = await service.get_all(skip=skip, limit=limit, search=search)
    total = await service.get_total_count(search=search)
    
    return {
        "suppliers": suppliers,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{supplier_id}", response_model=dict)
async def get_supplier(supplier_id: str):
    db = get_database()
    service = SupplierService(db)
    supplier = await service.get_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.post("", response_model=dict, status_code=201)
async def create_supplier(supplier: SupplierCreate):
    db = get_database()
    service = SupplierService(db)
    return await service.create(supplier)

@router.put("/{supplier_id}", response_model=dict)
async def update_supplier(supplier_id: str, supplier: SupplierUpdate):
    db = get_database()
    service = SupplierService(db)
    updated = await service.update(supplier_id, supplier)
    if not updated:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return updated

@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: str):
    db = get_database()
    service = SupplierService(db)
    deleted = await service.delete(supplier_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}