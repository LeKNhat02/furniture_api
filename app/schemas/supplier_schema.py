from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=255, description="Contact person name", alias="contactPerson")
    bank_account: Optional[str] = None
    tax_code: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True