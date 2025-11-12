from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(BaseModel):
    # Core customer fields - MATCH FRONTEND EXACTLY  
    id: str  # String type for frontend compatibility
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    # Frontend expects these computed fields (camelCase)
    totalSpent: float = 0.0  # camelCase for frontend compatibility
    totalOrders: int = 0     # camelCase for frontend compatibility
    
    # Status and metadata (camelCase)
    isActive: bool = True    # camelCase for frontend compatibility
    notes: Optional[str] = None
    createdAt: datetime      # camelCase for frontend
    updatedAt: datetime      # camelCase for frontend
    
    class Config:
        from_attributes = True

