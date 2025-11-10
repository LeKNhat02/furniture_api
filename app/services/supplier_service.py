from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.models import Supplier
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate
from fastapi import HTTPException, status
from typing import List

class SupplierService:
    @staticmethod
    def create_supplier(db: Session, supplier_data: SupplierCreate) -> Supplier:
        supplier = Supplier(**supplier_data.dict())
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier
    
    @staticmethod
    def get_all_suppliers(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str = ""
    ) -> List[Supplier]:
        query = db.query(Supplier)
        
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
    
    @staticmethod
    def get_supplier_by_id(db: Session, supplier_id: int) -> Supplier:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        return supplier
    
    @staticmethod
    def update_supplier(
        db: Session,
        supplier_id: int,
        supplier_data: SupplierUpdate
    ) -> Supplier:
        supplier = SupplierService.get_supplier_by_id(db, supplier_id)
        
        for key, value in supplier_data.dict(exclude_unset=True).items():
            setattr(supplier, key, value)
        
        db.commit()
        db.refresh(supplier)
        return supplier
    
    @staticmethod
    def delete_supplier(db: Session, supplier_id: int):
        supplier = SupplierService.get_supplier_by_id(db, supplier_id)
        db.delete(supplier)
        db.commit()
