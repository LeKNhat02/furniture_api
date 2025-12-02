from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class PromotionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    discount_type: str = Field(..., pattern="^(PERCENTAGE|FIXED)$", alias="discountType")
    discount_value: float = Field(..., gt=0, alias="discountValue")
    min_purchase: Optional[float] = Field(None, ge=0, description="Minimum purchase amount", alias="minPurchase")
    max_discount: Optional[float] = Field(None, gt=0, description="Maximum discount amount", alias="maxDiscount")
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
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
        populate_by_name = True