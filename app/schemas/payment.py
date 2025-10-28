from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    sale_id: str
    payment_method: str
    amount: float
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: str = Field(alias="_id")
    payment_date: datetime
    created_by: str
    created_at: datetime
    
    class Config:
        populate_by_name = True