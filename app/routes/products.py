from fastapi import APIRouter, HTTPException, Query
from app.database.db import get_database
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from typing import Optional

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=dict)
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True)
):
    db = get_database()
    service = ProductService(db)
    
    products = await service.get_all(
        skip=skip, 
        limit=limit, 
        search=search, 
        category=category,
        is_active=is_active
    )
    total = await service.get_total_count(search=search, category=category, is_active=is_active)
    
    return {
        "products": products,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: str):
    db = get_database()
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("", response_model=dict, status_code=201)
async def create_product(product: ProductCreate):
    db = get_database()
    service = ProductService(db)
    return await service.create(product)

@router.put("/{product_id}", response_model=dict)
async def update_product(product_id: str, product: ProductUpdate):
    db = get_database()
    service = ProductService(db)
    updated = await service.update(product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    db = get_database()
    service = ProductService(db)
    deleted = await service.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}