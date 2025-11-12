from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.supplier import Supplier
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate


class SupplierRepository(BaseRepository[Supplier, SupplierCreate, SupplierUpdate]):
    """Repository cho Supplier operations"""
    
    def __init__(self):
        super().__init__(Supplier)
    
    def get_active_suppliers(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Supplier]:
        """Get all active suppliers"""
        return db.query(Supplier).filter(
            Supplier.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Supplier]:
        """Get supplier by email"""
        return db.query(Supplier).filter(Supplier.email == email).first()
    
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[Supplier]:
        """Get supplier by phone"""
        return db.query(Supplier).filter(Supplier.phone == phone).first()
    
    def search_suppliers(
        self, 
        db: Session, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Supplier]:
        """Search suppliers by name, contact person, or company info"""
        return self.search(
            db=db,
            search_term=search_term,
            search_fields=["name", "contact_person", "email", "phone"],
            skip=skip,
            limit=limit
        )


# Create singleton instance  
supplier_repository = SupplierRepository()
