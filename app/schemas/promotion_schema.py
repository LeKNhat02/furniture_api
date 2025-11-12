from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class PromotionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    discount_type: str = Field(..., pattern="^(percentage|fixed_amount|PERCENTAGE|FIXED)$")
    discount_value: float = Field(..., gt=0)
    min_purchase: Optional[float] = Field(None, ge=0)  # Add missing frontend field
    max_discount: Optional[float] = Field(None, ge=0)   # Add missing frontend field
    start_date: date
    end_date: date
    is_active: bool = True

class PromotionCreate(PromotionBase):
    product_ids: Optional[List[int]] = None

class PromotionUpdate(PromotionBase):
    product_ids: Optional[List[int]] = None

class PromotionResponse(BaseModel):
    # Match frontend PromotionModel exactly
    id: str  # String type for frontend compatibility
    name: str
    description: Optional[str] = None
    discountType: str  # camelCase
    discountValue: float  # camelCase
    minPurchase: Optional[float] = None  # camelCase
    maxDiscount: Optional[float] = None  # camelCase
    startDate: datetime  # camelCase + DateTime instead of date
    endDate: datetime    # camelCase + DateTime instead of date
    isActive: bool       # camelCase
    createdAt: Optional[datetime] = None  # camelCase
    updatedAt: Optional[datetime] = None  # camelCase
    
    class Config:
        from_attributes = True