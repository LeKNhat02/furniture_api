from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=100, description="SKU/Product Code")
    description: Optional[str] = None
    category: Optional[str] = None
    price: float = Field(..., gt=0)
    cost: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None
    supplier_id: Optional[int] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None
    supplier_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Inventory fields from JOIN
    quantity: int = Field(default=0, description="Current stock quantity")
    quantity_min: int = Field(default=10, description="Minimum stock level", alias="quantityMin")
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both quantity_min and quantityMin