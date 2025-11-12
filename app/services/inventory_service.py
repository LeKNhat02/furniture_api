from sqlalchemy.orm import Session
from app.database.models import Inventory, InventoryTransaction, Product, Supplier
from app.schemas.inventory_schema import InventoryTransactionCreate, InventoryTransactionResponse
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

class InventoryService:
    @staticmethod
    def get_inventory_by_product(db: Session, product_id: int) -> Inventory:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id
        ).first()
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory not found"
            )
        return inventory
    
    @staticmethod
    def add_transaction(
        db: Session,
        transaction_data: InventoryTransactionCreate
    ) -> Inventory:
        inventory = InventoryService.get_inventory_by_product(
            db, transaction_data.product_id
        )
        
        # Update quantity based on transaction type
        if transaction_data.transaction_type == "IN":
            inventory.quantity_on_hand += transaction_data.quantity
        elif transaction_data.transaction_type == "OUT":
            if inventory.quantity_on_hand < transaction_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock"
                )
            inventory.quantity_on_hand -= transaction_data.quantity
        elif transaction_data.transaction_type == "ADJUSTMENT":
            inventory.quantity_on_hand = transaction_data.quantity
        
        # Record transaction with supplier info
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            product_id=transaction_data.product_id,  # Add product_id field
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            reason=transaction_data.reason,
            reference_number=transaction_data.reference_number,
            notes=transaction_data.notes,
            supplier_id=transaction_data.supplier_id  # Add supplier support
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(inventory)
        return inventory
    
    @staticmethod
    def get_low_stock_products(db: Session) -> List[Inventory]:
        return db.query(Inventory).filter(
            Inventory.quantity_on_hand <= Inventory.reorder_level
        ).all()
    
    @staticmethod
    def get_inventory_list(db: Session, skip: int = 0, limit: int = 100) -> List[Inventory]:
        return db.query(Inventory).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_transactions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        product_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[InventoryTransactionResponse]:
        """Get inventory transactions with filters and transform to frontend format"""
        query = (
            db.query(
                InventoryTransaction,
                Product.name.label("product_name"),
                Supplier.company_name.label("supplier_name")
            )
            .join(Product, InventoryTransaction.product_id == Product.id)
            .outerjoin(Supplier, InventoryTransaction.supplier_id == Supplier.id)
        )
        
        if product_id:
            query = query.filter(InventoryTransaction.product_id == product_id)
        
        if transaction_type:
            query = query.filter(
                InventoryTransaction.transaction_type == transaction_type
            )
        
        if start_date:
            query = query.filter(InventoryTransaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(InventoryTransaction.created_at <= end_date)
        
        results = query.order_by(
            InventoryTransaction.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        # Transform to frontend format
        return [
            InventoryService._transform_transaction_response(transaction, product_name, supplier_name)
            for transaction, product_name, supplier_name in results
        ]
    
    @staticmethod
    def _transform_transaction_response(
        transaction: InventoryTransaction,
        product_name: str = "",
        supplier_name: str = ""
    ) -> InventoryTransactionResponse:
        """Transform database model to frontend-compatible response"""
        return InventoryTransactionResponse(
            id=str(transaction.id),  # Convert to String
            productId=str(transaction.product_id),  # camelCase + String
            productName=product_name or "",  # Include product name
            type=transaction.transaction_type,  # Frontend uses 'type'
            quantity=transaction.quantity,
            reason=transaction.reason,
            notes=transaction.notes,
            supplierId=str(transaction.supplier_id) if transaction.supplier_id else None,  # camelCase + String
            date=transaction.created_at,  # Frontend field name
            createdBy=None,  # Will be set when user auth is added
            createdAt=transaction.created_at  # camelCase
        )