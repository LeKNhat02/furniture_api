# Import all models from app/models
from app.models import (
    User,
    Product,
    Customer,
    Supplier,
    Inventory,
    InventoryTransaction,
    Sale,
    SaleItem,
    Promotion,
    promotion_product,
    Payment,
    Report,
)

# Export all models for backward compatibility
__all__ = [
    "User",
    "Product",
    "Customer",
    "Supplier",
    "Inventory",
    "InventoryTransaction",
    "Sale",
    "SaleItem",
    "Promotion",
    "promotion_product",
    "Payment",
    "Report",
]