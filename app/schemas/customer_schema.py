from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    total_spent: float = Field(default=0.0, description="Total amount spent", alias="totalSpent")
    total_orders: int = Field(default=0, description="Total number of orders", alias="totalOrders")
    
    class Config:
        from_attributes = True
        populate_by_name = True