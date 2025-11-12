from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SaleItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = Field(default=0, ge=0)

class SaleItemResponse(BaseModel):
    # Match frontend SaleItem exactly
    productId: str  # camelCase + String type for frontend
    productName: str = ""  # Include product name for frontend
    quantity: int
    price: float  # Match frontend field name (not unit_price)
    discount: float = 0.0
    
    # Computed fields that frontend calculates (remove @computed_field)
    itemSubtotal: float = 0.0  # Price * quantity (before discount)
    subtotal: float = 0.0      # Final amount after discount

    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    items: List[SaleItemCreate] = Field(..., min_items=1)
    discount: float = Field(default=0, ge=0)
    tax: float = Field(default=0, ge=0)
    notes: Optional[str] = None
    payment_method: str = Field(default="cash")  # Add payment method
    is_paid: bool = Field(default=False)  # Add payment status

class SaleUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(completed|pending|cancelled)$")
    notes: Optional[str] = None
    is_paid: Optional[bool] = None
    payment_method: Optional[str] = None

class SaleResponse(BaseModel):
    # Core fields matching frontend SaleModel exactly
    id: str  # Convert to String for frontend compatibility
    orderNumber: str  # camelCase (from invoice_number)
    customerId: Optional[str] = None  # camelCase + String type
    customerName: Optional[str] = None  # Include customer info
    customerPhone: Optional[str] = None  # Include customer info
    
    # Embedded items (not separate API call)
    items: List[SaleItemResponse] = []
    
    # Payment and status info
    paymentMethod: str = "cash"  # camelCase
    status: str = "pending"
    isPaid: bool = False  # camelCase
    notes: Optional[str] = None
    
    # Timestamps
    createdAt: datetime  # camelCase
    updatedAt: Optional[datetime] = None  # camelCase
    
    # Computed totals that frontend expects (remove @computed_field)
    subtotal: float = 0.0     # Total before discount
    totalDiscount: float = 0.0  # Total discount amount
    total: float = 0.0        # Final total after discount
    itemCount: int = 0        # Total quantity of items

    class Config:
        from_attributes = True