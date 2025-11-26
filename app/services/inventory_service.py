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
    def get_inventory_list(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get inventory list with product information"""
        inventories = db.query(Inventory).join(Product).offset(skip).limit(limit).all()
        
        result = []
        for inv in inventories:
            product = db.query(Product).filter(Product.id == inv.product_id).first()
            result.append({
                'id': str(inv.id),
                'product_id': str(inv.product_id),
                'product_name': product.name if product else f'Sản phẩm {inv.product_id}',
                'quantity': inv.quantity_on_hand,
                'reorder_level': inv.reorder_level,
                'last_updated': inv.last_updated.isoformat() if inv.last_updated else None
            })
        
        return result
    
    @staticmethod
    def get_transactions_list(db: Session, skip: int = 0, limit: int = 100, 
                              product_id: int = None, transaction_type: str = None) -> List[dict]:
        """Get inventory transactions with product information"""
        query = db.query(InventoryTransaction).join(
            Inventory, InventoryTransaction.inventory_id == Inventory.id
        )
        
        if product_id:
            query = query.filter(Inventory.product_id == product_id)
        
        if transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == transaction_type.upper())
        
        transactions = query.order_by(InventoryTransaction.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for trans in transactions:
            inventory = db.query(Inventory).filter(Inventory.id == trans.inventory_id).first()
            product = db.query(Product).filter(Product.id == inventory.product_id).first() if inventory else None
            
            result.append({
                'id': str(trans.id),
                'product_id': str(inventory.product_id) if inventory else '',
                'product_name': product.name if product else 'Unknown',
                'type': 'in' if trans.transaction_type == 'IN' else 'out',
                'quantity': trans.quantity,
                'reason': trans.reason or '',
                'notes': trans.notes,
                'date': trans.created_at.isoformat() if trans.created_at else None,
                'created_at': trans.created_at.isoformat() if trans.created_at else None
            })
        
        return result