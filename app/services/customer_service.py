from sqlalchemy.orm import Session
from app.database.models import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate
from fastapi import HTTPException, status
from typing import List, Optional

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_customer(self, customer_data: CustomerCreate):
        """Create a new customer"""
        # Check if email already exists
        if customer_data.email:
            existing = self.db.query(Customer).filter(Customer.email == customer_data.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Check if phone already exists
        if customer_data.phone:
            existing = self.db.query(Customer).filter(Customer.phone == customer_data.phone).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already exists"
                )
        
        customer_dict = customer_data.dict() if hasattr(customer_data, 'dict') else customer_data.__dict__
        customer = Customer(**customer_dict)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def get_all_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all customers with pagination"""
        return self.db.query(Customer).offset(skip).limit(limit).all()
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()
    
    def update_customer(self, customer_id: int, customer_data: CustomerUpdate):
        """Update customer information"""
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Check email uniqueness if being updated
        if customer_data.email and customer_data.email != customer.email:
            existing = self.db.query(Customer).filter(Customer.email == customer_data.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Check phone uniqueness if being updated
        if customer_data.phone and customer_data.phone != customer.phone:
            existing = self.db.query(Customer).filter(Customer.phone == customer_data.phone).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already exists"
                )
        
        update_dict = customer_data.dict(exclude_unset=True) if hasattr(customer_data, 'dict') else customer_data.__dict__
        for key, value in update_dict.items():
            if value is not None:
                setattr(customer, key, value)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def delete_customer(self, customer_id: int):
        """Delete customer"""
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        self.db.delete(customer)
        self.db.commit()
        return {"message": "Customer deleted successfully"}