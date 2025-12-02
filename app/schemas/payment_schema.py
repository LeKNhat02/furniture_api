from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    sale_id: int = Field(..., gt=0)
    payment_method: str = Field(..., description="Payment method: cash, card, bank_transfer, transfer, other")
    amount: float = Field(..., gt=0)
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        # Normalize to uppercase and handle common variations
        v_upper = v.upper()
        method_map = {
            'CASH': 'CASH',
            'CARD': 'CARD',
            'BANK_TRANSFER': 'BANK_TRANSFER',
            'TRANSFER': 'BANK_TRANSFER',  # Map transfer to bank_transfer
            'OTHER': 'OTHER',
        }
        normalized = method_map.get(v_upper)
        if not normalized:
            raise ValueError(f"Invalid payment method. Must be one of: cash, card, bank_transfer, transfer, other")
        return normalized

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
    
    # Customer info from JOIN
    customer_id: Optional[int] = Field(None, description="Customer ID from Sale", alias="customerId")
    customer_name: Optional[str] = Field(None, description="Customer name", alias="customerName")
    customer_phone: Optional[str] = Field(None, description="Customer phone", alias="customerPhone")
    sale_name: Optional[str] = Field(None, description="Sale invoice number", alias="saleName")
    
    class Config:
        from_attributes = True
        populate_by_name = True
