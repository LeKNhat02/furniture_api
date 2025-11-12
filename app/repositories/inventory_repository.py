from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.repositories.base_repository import BaseRepository
from app.models.inventory import Inventory, InventoryTransaction
from app.schemas.inventory_schema import InventoryCreate, InventoryUpdate


class InventoryRepository(BaseRepository[Inventory, InventoryCreate, InventoryUpdate]):
    """Repository cho Inventory operations"""
    
    def __init__(self):
        super().__init__(Inventory)
    
    def get_by_product_id(self, db: Session, *, product_id: int) -> Optional[Inventory]:
        """Get inventory by product ID"""
        return db.query(Inventory).filter(Inventory.product_id == product_id).first()
    
    def get_with_product(self, db: Session, *, id: int) -> Optional[Inventory]:
        """Get inventory with product details"""
        return db.query(Inventory).options(joinedload(Inventory.product)).filter(
            Inventory.id == id
        ).first()
    
    def get_low_stock_items(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Inventory]:
        """Get inventory items with low stock"""
        return db.query(Inventory).options(joinedload(Inventory.product)).filter(
            Inventory.quantity_on_hand <= Inventory.reorder_level
        ).offset(skip).limit(limit).all()
    
    def get_out_of_stock_items(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Inventory]:
        """Get inventory items that are out of stock"""
        return db.query(Inventory).options(joinedload(Inventory.product)).filter(
            Inventory.quantity_on_hand <= 0
        ).offset(skip).limit(limit).all()
    
    def update_quantity(
        self, 
        db: Session, 
        *, 
        product_id: int, 
        new_quantity: int,
        transaction_type: str = "ADJUSTMENT",
        reason: str = None,
        reference_number: str = None
    ) -> Optional[Inventory]:
        """Update inventory quantity and create transaction log"""
        inventory = self.get_by_product_id(db=db, product_id=product_id)
        if not inventory:
            return None
        
        old_quantity = inventory.quantity_on_hand
        inventory.quantity_on_hand = new_quantity
        
        # Create transaction record
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=new_quantity - old_quantity,
            reason=reason,
            reference_number=reference_number
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(inventory)
        
        return inventory
    
    def adjust_quantity(
        self, 
        db: Session, 
        *, 
        product_id: int, 
        quantity_change: int,
        transaction_type: str = "ADJUSTMENT",
        reason: str = None,
        reference_number: str = None
    ) -> Optional[Inventory]:
        """Adjust inventory quantity by a certain amount"""
        inventory = self.get_by_product_id(db=db, product_id=product_id)
        if not inventory:
            return None
        
        new_quantity = inventory.quantity_on_hand + quantity_change
        if new_quantity < 0:
            new_quantity = 0
        
        return self.update_quantity(
            db=db,
            product_id=product_id,
            new_quantity=new_quantity,
            transaction_type=transaction_type,
            reason=reason,
            reference_number=reference_number
        )


class InventoryTransactionRepository(BaseRepository[InventoryTransaction, dict, dict]):
    """Repository cho Inventory Transaction operations"""
    
    def __init__(self):
        super().__init__(InventoryTransaction)
    
    def get_by_product_id(
        self, 
        db: Session, 
        *, 
        product_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[InventoryTransaction]:
        """Get transactions for a specific product"""
        return db.query(InventoryTransaction).filter(
            InventoryTransaction.product_id == product_id
        ).order_by(desc(InventoryTransaction.created_at)).offset(skip).limit(limit).all()
    
    def get_by_type(
        self, 
        db: Session, 
        *, 
        transaction_type: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[InventoryTransaction]:
        """Get transactions by type"""
        return db.query(InventoryTransaction).filter(
            InventoryTransaction.transaction_type == transaction_type
        ).order_by(desc(InventoryTransaction.created_at)).offset(skip).limit(limit).all()
    
    def get_recent_transactions(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[InventoryTransaction]:
        """Get recent inventory transactions"""
        return db.query(InventoryTransaction).order_by(
            desc(InventoryTransaction.created_at)
        ).offset(skip).limit(limit).all()


# Create singleton instances
inventory_repository = InventoryRepository()
inventory_transaction_repository = InventoryTransactionRepository()
