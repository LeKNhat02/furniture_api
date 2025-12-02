from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.promotion_schema import (
    PromotionCreate, PromotionUpdate, PromotionResponse
)
from app.services.promotion_service import PromotionService
from app.core.security import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/promotions", tags=["Promotions"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_promotion(
    promotion_data: PromotionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new promotion"""
    try:
        service = PromotionService(db)
        promotion = service.create_promotion(promotion_data)
        return {
            "data": promotion,
            "message": "Promotion created successfully",
            "status_code": 201
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error creating promotion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_promotions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search by name"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all promotions with pagination, search, and filters"""
    try:
        skip = (page - 1) * limit
        service = PromotionService(db)
        promotions = service.get_all_promotions(skip, limit, search, is_active)
        total_count = service.get_promotions_count(search, is_active)
        return {
            "data": promotions,
            "message": "Promotions retrieved successfully",
            "status_code": 200,
            "page": page,
            "limit": limit,
            "total": total_count
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving promotions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/list")
async def get_active_promotions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get active promotions only"""
    try:
        service = PromotionService(db)
        promotions = service.get_active_promotions()
        return {
            "data": promotions,
            "message": "Active promotions retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving active promotions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{promotion_id}")
async def get_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get promotion by ID"""
    try:
        service = PromotionService(db)
        promotion = service.get_promotion_by_id(promotion_id)
        return {
            "data": promotion,
            "message": "Promotion retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving promotion {promotion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{promotion_id}")
async def update_promotion(
    promotion_id: int,
    promotion_data: PromotionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update promotion"""
    try:
        service = PromotionService(db)
        promotion = service.update_promotion(promotion_id, promotion_data)
        return {
            "data": promotion,
            "message": "Promotion updated successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error updating promotion {promotion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{promotion_id}")
async def delete_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete promotion"""
    try:
        service = PromotionService(db)
        service.delete_promotion(promotion_id)
        return {
            "data": None,
            "message": "Promotion deleted successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error deleting promotion {promotion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))