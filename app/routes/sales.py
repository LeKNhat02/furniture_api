import logging
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import Customer
from app.schemas.sale_schema import (
    SaleCreate, SaleUpdate, SaleResponse
)
from app.services.sale_service import SaleService
from app.core.security import get_current_user
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sales", tags=["sales"])

def _enrich_sale_with_customer_info(db: Session, sale):
    """Helper function to add customer info to sale response"""
    customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
    
    sale_dict = {
        "id": sale.id,
        "invoice_number": sale.invoice_number,
        "order_number": sale.invoice_number,  # Alias for frontend compatibility
        "customer_id": sale.customer_id,
        "customer_name": customer.name if customer else None,
        "customer_phone": customer.phone if customer else None,
        "user_id": sale.user_id,
        "sale_date": sale.sale_date,
        "total_amount": sale.total_amount,
        "discount": sale.discount,
        "tax": sale.tax,
        "final_amount": sale.final_amount,
        "status": sale.status,
        "notes": sale.notes,
        "items": sale.items,
        "created_at": sale.created_at,
        "updated_at": sale.updated_at,
    }
    return sale_dict

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
        
        # Enrich with customer info
        enriched = _enrich_sale_with_customer_info(db, result)
        
        return {
            "data": enriched,
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
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search by invoice number or customer name"),
    status_filter: str = Query(None, description="Filter by status: completed, pending, cancelled"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all sales with pagination, search and filters"""
    try:
        skip = (page - 1) * limit
        logger.info(f"Fetching sales: page={page}, limit={limit}, search={search}, status={status_filter}")
        service = SaleService(db)
        sales_list = service.get_all_sales(skip, limit, search=search, status_filter=status_filter)
        total_count = service.get_sales_count(search=search, status_filter=status_filter)
        logger.info(f"Retrieved {len(sales_list)} sales")
        
        # Enrich all sales with customer info
        enriched_sales = [_enrich_sale_with_customer_info(db, s) for s in sales_list]
        
        return {
            "data": enriched_sales,
            "message": "Sales retrieved successfully",
            "status_code": 200,
            "page": page,
            "limit": limit,
            "total": total_count
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
        
        # Enrich with customer info
        enriched = _enrich_sale_with_customer_info(db, sale)
        
        return {
            "data": enriched,
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
        
        # Enrich with customer info
        enriched = _enrich_sale_with_customer_info(db, result)
        
        return {
            "data": enriched,
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