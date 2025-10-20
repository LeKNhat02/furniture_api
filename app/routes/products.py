from fastapi import APIRouter, Depends, HTTPException
from app.database.db import get_database
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=list[dict])
async def get_products():
    db = get_database()
    service = ProductService(db)
    return await service.get_all()

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