from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    sale_id: int = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(CASH|CARD|BANK_TRANSFER|OTHER)$")
    amount: float = Field(..., gt=0)
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: str = Field(..., pattern="^(completed|pending|failed)$")
    notes: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
