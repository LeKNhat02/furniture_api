from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Payment(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    sale_id: str
    payment_method: str  # "cash", "card", "transfer", "installment"
    amount: float
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    reference_number: Optional[str] = None  # Số tham chiếu (cho chuyển khoản, thẻ)
    notes: Optional[str] = None
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True