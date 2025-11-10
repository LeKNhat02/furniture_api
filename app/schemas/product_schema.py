from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True