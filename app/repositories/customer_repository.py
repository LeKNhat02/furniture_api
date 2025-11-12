from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.customer import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate


class CustomerRepository(BaseRepository[Customer, CustomerCreate, CustomerUpdate]):
    """Repository cho Customer operations"""
    
    def __init__(self):
        super().__init__(Customer)
    
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[Customer]:
        """Get customer by phone number"""
        return db.query(Customer).filter(Customer.phone == phone).first()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Customer]:
        """Get customer by email"""
        return db.query(Customer).filter(Customer.email == email).first()
    
    def get_active_customers(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Get all active customers"""
        return db.query(Customer).filter(
            Customer.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def get_by_city(
        self, 
        db: Session, 
        *, 
        city: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Get customers by city"""
        return db.query(Customer).filter(
            Customer.city == city,
            Customer.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def search_customers(
        self, 
        db: Session, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Search customers by name, phone, email, or address"""
        return self.search(
            db=db,
            search_term=search_term,
            search_fields=["name", "phone", "email", "address"],
            skip=skip,
            limit=limit
        )
    
    def get_customers_with_sales_history(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Get customers who have made purchases"""
        from app.models.sale import Sale
        
        return db.query(Customer).join(Sale).filter(
            Customer.is_active.is_(True)
        ).distinct().offset(skip).limit(limit).all()


# Create singleton instance
customer_repository = CustomerRepository()
