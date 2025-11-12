from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    payment_method = Column(String(50), nullable=False)  # CASH, CARD, BANK_TRANSFER
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, server_default=func.now())
    status = Column(String(50), default="completed")  # completed, pending, failed
    reference_number = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    sale = relationship("Sale", back_populates="payments")
