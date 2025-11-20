import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.product_schema import ProductCreate, ProductResponse
from app.schemas.response_schema import DataResponse, ListDataResponse
from app.services.product_service import ProductService
from app.core.security import get_current_user
from app.utils.validators import validate_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["products"])


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
        return {
            "data": result,
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
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all active products with pagination."""
    try:
        logger.info(f"Fetching products with skip={skip}, limit={limit}")
        service = ProductService(db)
        products = service.get_all_products(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(products)} products")
        return {
            "data": products,
            "message": "Products retrieved successfully",
            "status_code": 200
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
        return {
            "data": product,
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
    product_update: ProductCreate = None,
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
        return {
            "data": updated,
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