from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class PromotionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    discount_type: str = Field(..., pattern="^(PERCENTAGE|FIXED)$")
    discount_value: float = Field(..., gt=0)
    start_date: date
    end_date: date
    is_active: bool = True

class PromotionCreate(PromotionBase):
    product_ids: Optional[List[int]] = None

class PromotionUpdate(PromotionBase):
    product_ids: Optional[List[int]] = None

class PromotionResponse(PromotionBase):
    id: int
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True