from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.core.security import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.post("/", response_model=ProductResponse)
def create_product(
    name: str = Form(...),
    code: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: float = Form(...),
    cost: Optional[float] = Form(None),
    supplier_id: Optional[int] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new product with optional image upload"""
    product_data = ProductCreate(
        name=name,
        code=code,
        description=description,
        category=category,
        price=price,
        cost=cost,
        supplier_id=supplier_id,
        is_active=is_active,
        image_url=None
    )
    
    product = ProductService.create_product(db, product_data)
    
    # Handle image upload if provided
    if image:
        image_url = ProductService.save_product_image(image, product.id)
        product.image_url = image_url
        db.commit()
        db.refresh(product)
    
    return product

@router.get("/", response_model=List[ProductResponse])
def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all products with pagination and search"""
    skip = (page - 1) * limit
    return ProductService.get_all_products(db, skip, limit, search)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return ProductService.get_product_by_id(db, product_id)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return ProductService.update_product(db, product_id, product_data)

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return ProductService.delete_product(db, product_id)