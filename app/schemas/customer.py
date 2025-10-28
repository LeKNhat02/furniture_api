from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    customer_type: str = "regular"
    notes: Optional[str] = None
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: str = Field(alias="_id")
    total_spent: float = 0.0
    total_orders: int = 0
    last_order_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True