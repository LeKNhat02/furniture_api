from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database.db import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    report_type = Column(String(100), nullable=False)  # sales, inventory, customer, financial
    description = Column(Text)
    filters = Column(JSON)  # Store filter parameters as JSON
    data = Column(JSON)  # Store report data as JSON
    generated_by = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
