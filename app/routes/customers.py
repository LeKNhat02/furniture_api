import logging
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.db import get_db
from app.database.models import Sale
from app.schemas.customer_schema import (
    CustomerCreate, CustomerUpdate, CustomerResponse
)
from app.services.customer_service import CustomerService
from app.core.security import get_current_user
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/customers", tags=["customers"])

def _enrich_customer_with_sales_data(db: Session, customer):
    """Helper function to add sales statistics to customer response"""
    # Calculate total spent and total orders
    sales_stats = db.query(
        func.count(Sale.id).label('total_orders'),
        func.coalesce(func.sum(Sale.final_amount), 0).label('total_spent')
    ).filter(
        Sale.customer_id == customer.id,
        Sale.status != 'cancelled'
    ).first()
    
    customer_dict = {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
        "country": customer.country,
        "created_at": customer.created_at,
        "updated_at": customer.updated_at,
        "total_spent": float(sales_stats.total_spent) if sales_stats else 0.0,
        "total_orders": sales_stats.total_orders if sales_stats else 0,
    }
    return customer_dict

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new customer"""
    try:
        logger.info(f"Creating new customer")
        service = CustomerService(db)
        result = service.create_customer(customer_data)
        logger.info(f"Customer created successfully with ID: {result.id}")
        
        # Enrich with sales data
        enriched = _enrich_customer_with_sales_data(db, result)
        
        return {
            "data": enriched,
            "message": "Customer created successfully",
            "status_code": 201
        }
    except HTTPException as e:
        logger.warning(f"HTTP error creating customer: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer"
        )

@router.get("/")
async def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search by name, phone, or email"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all customers with pagination and search"""
    try:
        skip = (page - 1) * limit
        logger.info(f"Fetching customers: page={page}, limit={limit}, search={search}")
        service = CustomerService(db)
        customers_list = service.get_all_customers(skip, limit)
        total_count = service.get_customers_count()
        logger.info(f"Retrieved {len(customers_list)} customers")
        
        # Enrich all customers with sales data
        enriched_customers = [_enrich_customer_with_sales_data(db, c) for c in customers_list]
        
        return {
            "data": enriched_customers,
            "message": "Customers retrieved successfully",
            "status_code": 200,
            "page": page,
            "limit": limit,
            "total": total_count
        }
    except HTTPException as e:
        logger.warning(f"HTTP error fetching customers: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customers"
        )

@router.get("/{customer_id}")
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get customer by ID"""
    try:
        logger.info(f"Fetching customer {customer_id}")
        service = CustomerService(db)
        customer = service.get_customer_by_id(customer_id)
        if not customer:
            logger.warning(f"Customer not found: {customer_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found"
            )
        logger.info(f"Customer found: {customer_id}")
        
        # Enrich with sales data
        enriched = _enrich_customer_with_sales_data(db, customer)
        
        return {
            "data": enriched,
            "message": "Customer retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer"
        )

@router.put("/{customer_id}")
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update customer"""
    try:
        logger.info(f"Updating customer {customer_id}")
        service = CustomerService(db)
        result = service.update_customer(customer_id, customer_data)
        logger.info(f"Customer updated successfully: {customer_id}")
        
        # Enrich with sales data
        enriched = _enrich_customer_with_sales_data(db, result)
        
        return {
            "data": enriched,
            "message": "Customer updated successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error updating customer: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error updating customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update customer"
        )

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete customer"""
    try:
        logger.info(f"Deleting customer {customer_id}")
        service = CustomerService(db)
        service.delete_customer(customer_id)
        logger.info(f"Customer deleted successfully: {customer_id}")
        return {
            "data": None,
            "message": "Customer deleted successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error deleting customer: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error deleting customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete customer"
        )
