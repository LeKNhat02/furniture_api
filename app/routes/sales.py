import logging
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.sale_schema import (
    SaleCreate, SaleUpdate, SaleResponse
)
from app.services.sale_service import SaleService
from app.core.security import get_current_user
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sales", tags=["sales"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new sale"""
    try:
        logger.info(f"Creating new sale")
        service = SaleService(db)
        result = service.create_sale(sale_data, current_user.id)
        logger.info(f"Sale created successfully with ID: {result.id}")
        return {
            "data": result,
            "message": "Sale created successfully",
            "status_code": 201
        }
    except HTTPException as e:
        logger.warning(f"HTTP error creating sale: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error creating sale: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sale"
        )

@router.get("/")
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all sales"""
    try:
        logger.info(f"Fetching sales with skip={skip}, limit={limit}")
        service = SaleService(db)
        sales_list = service.get_all_sales(skip, limit)
        logger.info(f"Retrieved {len(sales_list)} sales")
        return {
            "data": sales_list,
            "message": "Sales retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error fetching sales: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error fetching sales: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sales"
        )

@router.get("/{sale_id}")
async def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sale by ID"""
    try:
        logger.info(f"Fetching sale {sale_id}")
        service = SaleService(db)
        sale = service.get_sale_by_id(sale_id)
        if not sale:
            logger.warning(f"Sale not found: {sale_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sale {sale_id} not found"
            )
        logger.info(f"Sale found: {sale_id}")
        return {
            "data": sale,
            "message": "Sale retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error fetching sale: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sale"
        )

@router.put("/{sale_id}")
async def update_sale(
    sale_id: int,
    sale_data: SaleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update sale status or notes"""
    try:
        logger.info(f"Updating sale {sale_id}")
        service = SaleService(db)
        result = service.update_sale(sale_id, sale_data)
        logger.info(f"Sale updated successfully: {sale_id}")
        return {
            "data": result,
            "message": "Sale updated successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error updating sale: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error updating sale: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sale"
        )

@router.delete("/{sale_id}")
async def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete (cancel) sale and restore inventory"""
    try:
        logger.info(f"Deleting sale {sale_id}")
        service = SaleService(db)
        service.delete_sale(sale_id)
        logger.info(f"Sale deleted successfully: {sale_id}")
        return {
            "data": None,
            "message": "Sale deleted successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error deleting sale: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error deleting sale: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sale"
        )