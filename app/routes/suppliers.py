import logging
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.supplier_schema import (
    SupplierCreate, SupplierUpdate, SupplierResponse
)
from app.services.supplier_service import SupplierService
from app.core.security import get_current_user
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new supplier"""
    try:
        logger.info(f"Creating new supplier")
        service = SupplierService(db)
        result = service.create_supplier(supplier_data)
        logger.info(f"Supplier created successfully with ID: {result.id}")
        return {
            "data": result,
            "message": "Supplier created successfully",
            "status_code": 201
        }
    except HTTPException as e:
        logger.warning(f"HTTP error creating supplier: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error creating supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create supplier"
        )

@router.get("/")
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query("", max_length=255),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all suppliers with search"""
    try:
        logger.info(f"Fetching suppliers with skip={skip}, limit={limit}, search='{search}'")
        service = SupplierService(db)
        suppliers_list = service.get_all_suppliers(skip, limit, search)
        logger.info(f"Retrieved {len(suppliers_list)} suppliers")
        return {
            "data": suppliers_list,
            "message": "Suppliers retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error fetching suppliers: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error fetching suppliers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch suppliers"
        )

@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get supplier by ID"""
    try:
        logger.info(f"Fetching supplier {supplier_id}")
        service = SupplierService(db)
        supplier = service.get_supplier_by_id(supplier_id)
        if not supplier:
            logger.warning(f"Supplier not found: {supplier_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier {supplier_id} not found"
            )
        logger.info(f"Supplier found: {supplier_id}")
        return {
            "data": supplier,
            "message": "Supplier retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error fetching supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supplier"
        )

@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update supplier"""
    try:
        logger.info(f"Updating supplier {supplier_id}")
        service = SupplierService(db)
        result = service.update_supplier(supplier_id, supplier_data)
        logger.info(f"Supplier updated successfully: {supplier_id}")
        return {
            "data": result,
            "message": "Supplier updated successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error updating supplier: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error updating supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update supplier"
        )

@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete supplier"""
    try:
        logger.info(f"Deleting supplier {supplier_id}")
        service = SupplierService(db)
        service.delete_supplier(supplier_id)
        logger.info(f"Supplier deleted successfully: {supplier_id}")
        return {
            "data": None,
            "message": "Supplier deleted successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error deleting supplier: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error deleting supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete supplier"
        )