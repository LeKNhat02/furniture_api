from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Customer(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None  # "male", "female", "other"
    customer_type: str = "regular"  # "regular", "vip"
    total_spent: float = 0.0
    total_orders: int = 0
    last_order_date: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        schema_extra = {
            "example": {
                "name": "Nguyễn Văn A",
                "phone": "0123456789",
                "email": "nguyenvana@email.com",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "customer_type": "regular"
            }
        }