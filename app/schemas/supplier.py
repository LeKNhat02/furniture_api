from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SupplierBase(BaseModel):
    name: str
    contact_person: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    tax_code: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True