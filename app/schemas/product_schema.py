from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    cost: Optional[float] = None
    image_url: Optional[str] = None
    supplier_id: Optional[int] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    # Add sku field for creation
    sku: Optional[str] = None

class ProductUpdate(ProductBase):
    # Add sku field for updates
    sku: Optional[str] = None

class ProductResponse(BaseModel):
    # Core product fields - MATCH FRONTEND EXACTLY
    id: str  # String type for frontend compatibility
    name: str
    code: str
    sku: str  # Required field matching frontend
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    cost: Optional[float] = None
    
    # Frontend expects these inventory fields (camelCase)
    quantity: int = 0  # from inventory.quantity_on_hand
    quantityMin: int = 10  # from inventory.reorder_level (camelCase)
    
    # Image handling (camelCase)
    imageUrl: Optional[str] = None  # camelCase matching frontend
    
    # Status and metadata (camelCase)
    isActive: bool = True  # camelCase matching frontend
    createdAt: datetime  # camelCase for frontend
    updatedAt: datetime  # camelCase for frontend
    
    # Computed fields that frontend expects
    profit: float = 0.0  # Computed: price - cost
    isLowStock: bool = False  # Computed: quantity <= quantityMin
    
    class Config:
        from_attributes = True