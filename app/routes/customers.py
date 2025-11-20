import logging
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.customer_schema import (
    CustomerCreate, CustomerUpdate, CustomerResponse
)
from app.services.customer_service import CustomerService
from app.core.security import get_current_user
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/customers", tags=["customers"])

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
        return {
            "data": result,
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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all customers"""
    try:
        logger.info(f"Fetching customers with skip={skip}, limit={limit}")
        service = CustomerService(db)
        customers_list = service.get_all_customers(skip, limit)
        logger.info(f"Retrieved {len(customers_list)} customers")
        return {
            "data": customers_list,
            "message": "Customers retrieved successfully",
            "status_code": 200
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
        return {
            "data": customer,
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
        return {
            "data": result,
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
