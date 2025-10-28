from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PromotionBase(BaseModel):
    name: str
    description: Optional[str] = None
    promotion_type: str
    discount_value: float
    min_order_amount: Optional[float] = None
    max_discount_amount: Optional[float] = None
    applicable_products: Optional[list] = None
    start_date: datetime
    end_date: datetime
    usage_limit: Optional[int] = None
    is_active: bool = True

class PromotionCreate(PromotionBase):
    pass

class PromotionUpdate(PromotionBase):
    pass

class PromotionResponse(PromotionBase):
    id: str = Field(alias="_id")
    used_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True