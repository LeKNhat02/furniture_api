from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Date, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base


# Junction Table for Many-to-Many relationship
promotion_product = Table(
    'promotion_product',
    Base.metadata,
    Column('promotion_id', Integer, ForeignKey('promotions.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True)
)


class Promotion(Base):
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    discount_type = Column(String(50))  # percentage, fixed_amount
    discount_value = Column(Float, nullable=False)
    min_purchase = Column(Float, nullable=True)  # Add missing frontend field
    max_discount = Column(Float, nullable=True)   # Add missing frontend field
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships (Many-to-Many)
    products = relationship("Product", secondary="promotion_product", back_populates="promotions")
