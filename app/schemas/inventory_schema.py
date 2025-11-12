from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity_on_hand: int = Field(default=0, ge=0)
    quantity_reserved: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    reorder_quantity: int = Field(default=50, gt=0)

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity_on_hand: Optional[int] = Field(None, ge=0)
    quantity_reserved: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    reorder_quantity: Optional[int] = Field(None, gt=0)

class InventoryResponse(InventoryBase):
    id: int
    last_count_date: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InventoryTransactionCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ne=0)
    transaction_type: str = Field(..., pattern="^(IN|OUT|ADJUSTMENT)$")
    reason: str = Field(..., min_length=1, max_length=255)
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    supplier_id: Optional[int] = None  # Add supplier field for IN transactions

class InventoryTransactionResponse(BaseModel):
    # Match frontend InventoryTransaction model exactly
    id: str  # String type for frontend compatibility
    productId: str  # camelCase + String type
    productName: str = ""  # Include product name for frontend
    type: str  # Frontend uses 'type' not 'transaction_type'
    quantity: int
    reason: str
    notes: Optional[str] = None
    supplierId: Optional[str] = None  # camelCase + String type
    date: datetime  # Frontend field name
    createdBy: Optional[str] = None  # Frontend field
    createdAt: datetime  # camelCase
    
    class Config:
        from_attributes = True