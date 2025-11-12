from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.models import Supplier
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate, SupplierResponse
from fastapi import HTTPException, status

class SupplierService:
    @staticmethod
    def create_supplier(db: Session, supplier_data: SupplierCreate):
        supplier = Supplier(**supplier_data.dict())
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        
        # Return with frontend-compatible field names
        return SupplierService._transform_supplier_response(supplier)
    
    @staticmethod
    def get_all_suppliers(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str = ""
    ):
        query = db.query(Supplier).filter(Supplier.is_active)
        
        if search:
            query = query.filter(
                or_(
                    Supplier.name.contains(search),
                    Supplier.email.contains(search),
                    Supplier.phone.contains(search),
                    Supplier.city.contains(search),
                    Supplier.contact_person.contains(search)
                )
            )
        
        suppliers = query.offset(skip).limit(limit).all()
        
        # Transform all suppliers for frontend compatibility
        result = []
        for supplier in suppliers:
            result.append(SupplierService._transform_supplier_response(supplier))
        
        return result
    
    @staticmethod
    def get_supplier_by_id(db: Session, supplier_id: int):
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        return SupplierService._transform_supplier_response(supplier)
    
    @staticmethod
    def update_supplier(
        db: Session,
        supplier_id: int,
        supplier_data: SupplierUpdate
    ):
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        for key, value in supplier_data.dict(exclude_unset=True).items():
            setattr(supplier, key, value)
        
        db.commit()
        db.refresh(supplier)
        
        return SupplierService._transform_supplier_response(supplier)
    
    @staticmethod
    def delete_supplier(db: Session, supplier_id: int):
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        # Soft delete by setting is_active = False
        supplier.is_active = False
        db.commit()
        return {"message": "Supplier deleted successfully"}
    
    @staticmethod
    def _transform_supplier_response(supplier: Supplier) -> SupplierResponse:
        """Transform supplier to match frontend expectations"""
        return SupplierResponse(
            id=str(supplier.id),  # Convert to String for frontend compatibility
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            city=supplier.city,
            country=supplier.country,
            contactPerson=supplier.contact_person,  # camelCase
            notes=supplier.notes,
            bankAccount=supplier.bank_account,  # camelCase
            taxCode=supplier.tax_code,          # camelCase
            isActive=supplier.is_active,        # camelCase
            createdAt=supplier.created_at,      # camelCase
            updatedAt=supplier.updated_at       # camelCase
        )
