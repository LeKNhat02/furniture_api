from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Promotion(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    description: Optional[str] = None
    promotion_type: str  # "percentage", "fixed_amount", "buy_x_get_y"
    discount_value: float  # Giá trị giảm (% hoặc số tiền)
    min_order_amount: Optional[float] = None  # Đơn hàng tối thiểu
    max_discount_amount: Optional[float] = None  # Giảm tối đa
    applicable_products: Optional[list] = None  # Danh sách product_id áp dụng
    start_date: datetime
    end_date: datetime
    usage_limit: Optional[int] = None  # Giới hạn số lần sử dụng
    used_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        schema_extra = {
            "example": {
                "name": "Giảm giá 20% tất cả sản phẩm",
                "promotion_type": "percentage",
                "discount_value": 20,
                "min_order_amount": 1000000,
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-01-31T23:59:59"
            }
        }