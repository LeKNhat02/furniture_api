from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SaleItemBase(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    discount_amount: float = 0.0
    total_price: float

class SaleBase(BaseModel):
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    items: List[SaleItemBase]
    subtotal: float
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    total_amount: float
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class SaleCreate(SaleBase):
    pass

class SaleUpdate(BaseModel):
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class SaleResponse(SaleBase):
    id: str = Field(alias="_id")
    sale_number: str
    payment_status: str
    sale_date: datetime
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True