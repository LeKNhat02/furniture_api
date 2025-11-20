from sqlalchemy.orm import Session
from app.database.models import Inventory, InventoryTransaction, Product
from app.schemas.inventory_schema import InventoryTransactionCreate
from fastapi import HTTPException, status
from typing import List

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
        
        # Update quantity
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
        
        # Record transaction
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            reason=transaction_data.reason,
            reference_number=transaction_data.reference_number,
            notes=transaction_data.notes
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