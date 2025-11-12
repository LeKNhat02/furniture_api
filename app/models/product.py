from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)
    sku = Column(String(100), unique=True, index=True, nullable=True)  # Added SKU field
    description = Column(Text)
    category = Column(String(100))
    price = Column(Float, nullable=False)
    cost = Column(Float)
    image_url = Column(String(500))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    sale_items = relationship("SaleItem", back_populates="product")
    promotions = relationship("Promotion", back_populates="products", secondary="promotion_product")
