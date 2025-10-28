from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SaleItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    discount_amount: float = 0.0
    total_price: float

class Sale(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    sale_number: str  # Mã đơn hàng (auto-generated)
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    items: List[SaleItem]
    subtotal: float
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    total_amount: float
    payment_status: str = "pending"  # "pending", "partial", "paid", "refunded"
    payment_method: Optional[str] = None  # "cash", "card", "transfer", "installment"
    notes: Optional[str] = None
    sale_date: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True