import logging
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.inventory_schema import (
    InventoryResponse, InventoryTransactionCreate, InventoryTransactionResponse
)
from app.services.inventory_service import InventoryService
from app.core.security import get_current_user
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/inventory", tags=["inventory"])

@router.get("/")
async def get_inventory_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all inventory"""
    try:
        logger.info(f"Fetching inventory with skip={skip}, limit={limit}")
        inventory_list = InventoryService.get_inventory_list(db, skip, limit)
        logger.info(f"Retrieved {len(inventory_list)} inventory items")
        return {
            "data": inventory_list,
            "message": "Inventory retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error fetching inventory: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch inventory"
        )

@router.get("/product/{product_id}")
async def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory for a specific product"""
    try:
        logger.info(f"Fetching inventory for product {product_id}")
        inventory = InventoryService.get_inventory_by_product(db, product_id)
        if not inventory:
            logger.warning(f"Inventory not found for product {product_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory not found for product {product_id}"
            )
        logger.info(f"Inventory found for product {product_id}")
        return {
            "data": inventory,
            "message": "Inventory retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch inventory"
        )

@router.post("/transaction", status_code=status.HTTP_201_CREATED)
async def add_inventory_transaction(
    transaction: InventoryTransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add inventory transaction (IN, OUT, ADJUSTMENT)"""
    try:
        logger.info(f"Adding inventory transaction: {transaction.transaction_type}")
        result = InventoryService.add_transaction(db, transaction)
        logger.info(f"Transaction added successfully")
        return {
            "data": result,
            "message": "Transaction added successfully",
            "status_code": 201
        }
    except HTTPException as e:
        logger.warning(f"HTTP error adding transaction: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add transaction"
        )

@router.get("/transactions")
async def get_transactions_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    product_id: int = Query(None),
    transaction_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all inventory transactions with product names"""
    try:
        logger.info(f"Fetching transactions with skip={skip}, limit={limit}")
        transactions = InventoryService.get_transactions_list(
            db, skip, limit, product_id, transaction_type
        )
        logger.info(f"Retrieved {len(transactions)} transactions")
        return {
            "data": transactions,
            "message": "Transactions retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error fetching transactions: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions"
        )

@router.get("/low-stock/list")
async def get_low_stock(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get products with low stock"""
    try:
        logger.info("Fetching low stock products")
        low_stock = InventoryService.get_low_stock_products(db)
        logger.info(f"Found {len(low_stock)} low stock products")
        return {
            "data": low_stock,
            "message": "Low stock products retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        logger.warning(f"HTTP error fetching low stock: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error fetching low stock products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch low stock products"
        )