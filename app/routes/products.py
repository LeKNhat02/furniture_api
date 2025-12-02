import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import Inventory
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.response_schema import DataResponse, ListDataResponse
from app.services.product_service import ProductService
from app.core.security import get_current_user
from app.utils.validators import validate_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["products"])


def _enrich_product_with_inventory(db: Session, product):
    """Helper function to add inventory data to product response"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
    
    # Create dict from product
    product_dict = {
        "id": product.id,
        "name": product.name,
        "code": product.code,
        "description": product.description,
        "category": product.category,
        "price": product.price,
        "cost": product.cost,
        "image_url": product.image_url,
        "supplier_id": product.supplier_id,
        "is_active": product.is_active,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "sku": product.code,  # Frontend uses 'sku' field
        "quantity": inventory.quantity_on_hand if inventory else 0,
        "quantity_min": inventory.reorder_level if inventory else 10,
    }
    return product_dict


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new product. Requires authentication."""
    try:
        logger.info(f"Creating product: {product.name}")
        service = ProductService(db)
        result = service.create_product(product)
        logger.info(f"Product created successfully with ID: {result.id}")
        
        # Enrich with inventory data
        enriched = _enrich_product_with_inventory(db, result)
        
        return {
            "data": enriched,
            "message": "Product created successfully",
            "status_code": 201
        }
    except HTTPException as e:
        logger.warning(f"HTTP error creating product: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.get("/")
async def get_all_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search by name, code, or category"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all active products with pagination and search."""
    try:
        skip = (page - 1) * limit
        logger.info(f"Fetching products: page={page}, limit={limit}, search={search}")
        service = ProductService(db)
        products = service.get_all_products(skip=skip, limit=limit, search=search)
        total_count = service.get_products_count(search=search)
        logger.info(f"Retrieved {len(products)} products")
        
        # Enrich all products with inventory data
        enriched_products = [_enrich_product_with_inventory(db, p) for p in products]
        
        return {
            "data": enriched_products,
            "message": "Products retrieved successfully",
            "status_code": 200,
            "page": page,
            "limit": limit,
            "total": total_count
        }
    except HTTPException as e:
        logger.warning(f"HTTP error fetching products: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products"
        )



@router.get("/{product_id}")
async def get_product(
    product_id: int = Path(..., gt=0, description="Product ID must be a positive integer"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific product by ID. Product ID must be a positive integer."""
    try:
        validated_id = validate_id(product_id)
        logger.info(f"Fetching product with ID: {validated_id}")
        service = ProductService(db)
        product = service.get_product_by_id(validated_id)
        if not product:
            logger.warning(f"Product not found with ID: {validated_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {validated_id} not found"
            )
        logger.info(f"Product found: {product.name}")
        
        # Enrich with inventory data
        enriched = _enrich_product_with_inventory(db, product)
        
        return {
            "data": enriched,
            "message": "Product retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product"
        )


@router.put("/{product_id}")
async def update_product(
    product_id: int = Path(..., gt=0, description="Product ID must be a positive integer"),
    product_update: ProductUpdate = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing product. Requires authentication."""
    try:
        validated_id = validate_id(product_id)
        logger.info(f"Updating product with ID: {validated_id}")
        service = ProductService(db)
        
        # Check if product exists first
        existing = service.get_product_by_id(validated_id)
        if not existing:
            logger.warning(f"Product not found for update with ID: {validated_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {validated_id} not found"
            )
        
        updated = service.update_product(validated_id, product_update)
        logger.info(f"Product updated successfully: {updated.name}")
        
        # Enrich with inventory data
        enriched = _enrich_product_with_inventory(db, updated)
        
        return {
            "data": enriched,
            "message": "Product updated successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int = Path(..., gt=0, description="Product ID must be a positive integer"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete (soft delete) a product. Requires authentication."""
    try:
        validated_id = validate_id(product_id)
        logger.info(f"Deleting product with ID: {validated_id}")
        service = ProductService(db)
        
        # Check if product exists
        existing = service.get_product_by_id(validated_id)
        if not existing:
            logger.warning(f"Product not found for deletion with ID: {validated_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {validated_id} not found"
            )
        
        service.delete_product(validated_id)
        logger.info(f"Product deleted successfully with ID: {validated_id}")
        return {
            "data": None,
            "message": "Product deleted successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )
        logger.info(f"Product deleted successfully with ID: {validated_id}")
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )