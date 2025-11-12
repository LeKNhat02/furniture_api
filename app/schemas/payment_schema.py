from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    sale_id: int = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(cash|transfer|card|CASH|CARD|BANK_TRANSFER|OTHER)$")
    amount: float = Field(..., gt=0)
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: str = Field(..., pattern="^(completed|pending|failed)$")
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    # Match frontend PaymentModel exactly
    id: str  # String type for frontend compatibility
    saleId: str  # camelCase + String type
    saleName: Optional[str] = None  # Include sale reference info
    customerId: str  # camelCase + String type
    customerName: Optional[str] = None  # Include customer name
    amount: float
    paymentMethod: str  # camelCase, frontend uses cash/transfer
    status: str  # completed, pending, failed
    paymentDate: datetime  # camelCase
    transactionId: Optional[str] = None  # camelCase
    bankName: Optional[str] = None  # camelCase
    accountNumber: Optional[str] = None  # camelCase
    notes: Optional[str] = None
    createdAt: datetime  # camelCase
    updatedAt: Optional[datetime] = None  # camelCase
    
    class Config:
        from_attributes = True
