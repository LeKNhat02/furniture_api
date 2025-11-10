from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.promotion_schema import (
    PromotionCreate, PromotionUpdate, PromotionResponse
)
from app.services.promotion_service import PromotionService
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/promotions", tags=["Promotions"])

@router.post("/", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(
    promotion_data: PromotionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new promotion"""
    return PromotionService.create_promotion(db, promotion_data)

@router.get("/", response_model=List[PromotionResponse])
def get_promotions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all promotions"""
    return PromotionService.get_all_promotions(db, skip, limit)

@router.get("/active/list", response_model=List[PromotionResponse])
def get_active_promotions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get active promotions only"""
    return PromotionService.get_active_promotions(db)

@router.get("/{promotion_id}", response_model=PromotionResponse)
def get_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get promotion by ID"""
    return PromotionService.get_promotion_by_id(db, promotion_id)

@router.put("/{promotion_id}", response_model=PromotionResponse)
def update_promotion(
    promotion_id: int,
    promotion_data: PromotionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update promotion"""
    return PromotionService.update_promotion(db, promotion_id, promotion_data)

@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete promotion"""
    PromotionService.delete_promotion(db, promotion_id)
    return None
