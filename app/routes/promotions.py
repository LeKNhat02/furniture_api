from fastapi import APIRouter, HTTPException, Query
from app.database.db import get_database
from app.schemas.promotion import PromotionCreate, PromotionUpdate
from app.services.promotion_service import PromotionService
from typing import Optional

router = APIRouter(prefix="/promotions", tags=["promotions"])

@router.get("", response_model=dict)
async def get_promotions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    current_only: bool = Query(False)
):
    db = get_database()
    service = PromotionService(db)
    
    promotions = await service.get_all(
        skip=skip, 
        limit=limit, 
        is_active=is_active,
        current_only=current_only
    )
    total = await service.get_total_count(is_active=is_active, current_only=current_only)
    
    return {
        "promotions": promotions,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/applicable", response_model=list)
async def get_applicable_promotions(
    order_amount: float = Query(..., gt=0),
    product_ids: Optional[str] = Query(None)  # Comma-separated string
):
    """Lấy các khuyến mãi có thể áp dụng cho đơn hàng"""
    db = get_database()
    service = PromotionService(db)
    
    product_list = product_ids.split(",") if product_ids else None
    return await service.get_applicable_promotions(order_amount, product_list)

@router.get("/{promotion_id}", response_model=dict)
async def get_promotion(promotion_id: str):
    db = get_database()
    service = PromotionService(db)
    promotion = await service.get_by_id(promotion_id)
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promotion

@router.post("", response_model=dict, status_code=201)
async def create_promotion(promotion: PromotionCreate):
    db = get_database()
    service = PromotionService(db)
    return await service.create(promotion)

@router.put("/{promotion_id}", response_model=dict)
async def update_promotion(promotion_id: str, promotion: PromotionUpdate):
    db = get_database()
    service = PromotionService(db)
    updated = await service.update(promotion_id, promotion)
    if not updated:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return updated

@router.delete("/{promotion_id}")
async def delete_promotion(promotion_id: str):
    db = get_database()
    service = PromotionService(db)
    deleted = await service.delete(promotion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return {"message": "Promotion deleted successfully"}