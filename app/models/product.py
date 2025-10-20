from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Product(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    category: str
    price: float
    cost: float
    quantity: int = 0
    quantity_min: int = 10
    description: Optional[str] = None
    sku: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        schema_extra = {
            "example": {
                "name": "Bàn ăn gỗ",
                "category": "Bàn",
                "price": 5000000,
                "cost": 3000000,
                "quantity": 10,
                "quantity_min": 5,
                "description": "Bàn ăn 6 ghế",
                "sku": "SKU-001"
            }
        }