from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SaleItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = Field(default=0, ge=0)

class SaleItemResponse(SaleItemCreate):
    id: int
    sale_id: int
    line_price: float

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    customer_id: int
    total_amount: float = Field(..., gt=0)
    discount: float = Field(default=0, ge=0)
    tax: float = Field(default=0, ge=0)
    final_amount: float = Field(..., gt=0)
    status: str = Field(default="completed", pattern="^(completed|pending|canceled)$")
    notes: Optional[str] = None

class SaleCreate(SaleBase):
    items: List[SaleItemCreate]

class SaleUpdate(BaseModel):
     status: str = Field(..., pattern="^(completed|pending|canceled)$")
     notes: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    user_id: Optional[int] = None
    sale_date: datetime
    total_amount: float
    discount: float
    tax: float
    final_amount: float
    status: str
    notes: Optional[str] = None
    items: List[SaleItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True