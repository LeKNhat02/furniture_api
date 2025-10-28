from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Supplier(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    contact_person: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    tax_code: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    payment_terms: Optional[str] = None  # Điều kiện thanh toán
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        schema_extra = {
            "example": {
                "name": "Công ty TNHH Nội thất ABC",
                "contact_person": "Nguyễn Văn B",
                "phone": "0987654321",
                "email": "contact@noithat-abc.com",
                "address": "456 Đường XYZ, Quận 2, TP.HCM"
            }
        }