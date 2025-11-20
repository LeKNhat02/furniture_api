from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class RevenueReportItem(BaseModel):
    date: date
    total: float

class TopProductItem(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int
    total_sales: float

class CustomerReportItem(BaseModel):
    customer_id: int
    customer_name: str
    total_purchases: int
    total_spent: float

class InventoryReportItem(BaseModel):
    product_id: int
    product_name: str
    quantity_on_hand: int
    quantity_reserved: int
    reorder_level: int
    status: str  # OK, LOW, CRITICAL

class DashboardSummary(BaseModel):
    total_sales: float
    total_revenue: float
    total_customers: int
    total_products: int
    low_stock_count: int
    today_sales: float
    today_sales_count: int