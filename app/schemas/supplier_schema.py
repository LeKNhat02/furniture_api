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
    contact_person: Optional[str] = Field(None, max_length=255)  # Added for frontend compatibility
    bank_account: Optional[str] = Field(None, max_length=50)
    tax_code: Optional[str] = Field(None, max_length=50)

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierResponse(BaseModel):
    # Core supplier fields matching frontend SupplierModel EXACTLY
    id: str  # String type for frontend compatibility
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    contactPerson: Optional[str] = None  # camelCase for frontend compatibility
    notes: Optional[str] = None
    
    # Additional backend fields
    bankAccount: Optional[str] = None  # camelCase
    taxCode: Optional[str] = None      # camelCase
    
    # Status and metadata (camelCase)
    isActive: bool = True  # camelCase for frontend compatibility
    createdAt: datetime    # camelCase
    updatedAt: datetime    # camelCase
    
    class Config:
        from_attributes = True