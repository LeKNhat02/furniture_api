from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InventoryMovement(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    product_id: str
    movement_type: str  # "import", "export", "adjustment"
    quantity: int  # Số lượng (âm nếu xuất kho)
    reason: str  # "sale", "purchase", "return", "damaged", "adjustment"
    reference_id: Optional[str] = None  # ID của sale hoặc purchase order
    notes: Optional[str] = None
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True