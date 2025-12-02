from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity_on_hand: int = Field(default=0, ge=0)
    quantity_reserved: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    reorder_quantity: int = Field(default=50, gt=0)

class InventoryResponse(InventoryBase):
    id: int
    last_count_date: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InventoryTransactionCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ne=0)
    transaction_type: str = Field(..., description="Transaction type: in, out, or adjustment")
    reason: str = Field(..., min_length=1, max_length=255)
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        # Normalize to uppercase
        v_upper = v.upper()
        type_map = {
            'IN': 'IN',
            'OUT': 'OUT',
            'ADJUSTMENT': 'ADJUSTMENT',
        }
        normalized = type_map.get(v_upper)
        if not normalized:
            raise ValueError("Transaction type must be one of: in, out, adjustment")
        return normalized

class InventoryTransactionResponse(InventoryTransactionCreate):
    id: int
    inventory_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True