from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.models import Supplier
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate
from fastapi import HTTPException, status
from typing import List, Optional

class SupplierService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_supplier(self, supplier_data: SupplierCreate) -> Supplier:
        """Create a new supplier"""
        supplier_dict = supplier_data.dict() if hasattr(supplier_data, 'dict') else supplier_data.__dict__
        supplier = Supplier(**supplier_dict)
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier
    
    def get_all_suppliers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str = ""
    ) -> List[Supplier]:
        """Get all suppliers with optional search"""
        query = self.db.query(Supplier)
        
        if search:
            query = query.filter(
                or_(
                    Supplier.name.contains(search),
                    Supplier.email.contains(search),
                    Supplier.phone.contains(search),
                    Supplier.city.contains(search)
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_suppliers_count(self, search: str = "") -> int:
        """Get total count of suppliers with optional search filter"""
        query = self.db.query(Supplier)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Supplier.name.ilike(search_term)) |
                (Supplier.email.ilike(search_term)) |
                (Supplier.phone.ilike(search_term)) |
                (Supplier.city.ilike(search_term))
            )
        
        return query.count()

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID"""
        return self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
    
    def update_supplier(
        self,
        supplier_id: int,
        supplier_data: SupplierUpdate
    ) -> Supplier:
        """Update supplier information"""
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        update_dict = supplier_data.dict(exclude_unset=True) if hasattr(supplier_data, 'dict') else supplier_data.__dict__
        for key, value in update_dict.items():
            if value is not None:
                setattr(supplier, key, value)
        
        self.db.commit()
        self.db.refresh(supplier)
        return supplier
    
    def delete_supplier(self, supplier_id: int):
        """Delete supplier"""
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        self.db.delete(supplier)
        self.db.commit()
        return {"message": "Supplier deleted successfully"}
