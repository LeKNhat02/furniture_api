from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.repositories.base_repository import BaseRepository
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.product_schema import ProductCreate, ProductUpdate


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    """Repository cho Product operations với inventory support"""
    
    def __init__(self):
        super().__init__(Product)
    
    def get_with_inventory(self, db: Session, *, id: int) -> Optional[Product]:
        """Get product with inventory data"""
        return db.query(Product).options(joinedload(Product.inventory)).filter(Product.id == id).first()
    
    def get_multi_with_inventory(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Product]:
        """Get multiple products with inventory data"""
        query = db.query(Product).options(joinedload(Product.inventory))
        
        if active_only:
            query = query.filter(Product.is_active.is_(True))
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_code(self, db: Session, *, code: str) -> Optional[Product]:
        """Get product by code"""
        return db.query(Product).filter(Product.code == code).first()
    
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return db.query(Product).filter(Product.sku == sku).first()
    
    def get_by_category(
        self, 
        db: Session, 
        *, 
        category: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products by category"""
        return db.query(Product).options(joinedload(Product.inventory)).filter(
            Product.category == category,
            Product.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def search_products(
        self, 
        db: Session, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Search products with inventory by multiple fields"""
        search_conditions = [
            Product.name.ilike(f"%{search_term}%"),
            Product.code.ilike(f"%{search_term}%"),
            Product.sku.ilike(f"%{search_term}%"),
            Product.description.ilike(f"%{search_term}%"),
            Product.category.ilike(f"%{search_term}%")
        ]
        
        return db.query(Product).options(joinedload(Product.inventory)).filter(
            or_(*search_conditions),
            Product.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def get_low_stock_products(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products with low stock (quantity <= reorder_level)"""
        return db.query(Product).options(joinedload(Product.inventory)).join(
            Inventory, Product.id == Inventory.product_id
        ).filter(
            Inventory.quantity_on_hand <= Inventory.reorder_level,
            Product.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def get_out_of_stock_products(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products that are out of stock"""
        return db.query(Product).options(joinedload(Product.inventory)).join(
            Inventory, Product.id == Inventory.product_id
        ).filter(
            Inventory.quantity_on_hand <= 0,
            Product.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def get_by_supplier(
        self, 
        db: Session, 
        *, 
        supplier_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products by supplier"""
        return db.query(Product).options(joinedload(Product.inventory)).filter(
            Product.supplier_id == supplier_id,
            Product.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def create_with_inventory(
        self, 
        db: Session, 
        *, 
        product_data: ProductCreate,
        initial_quantity: int = 0,
        reorder_level: int = 10
    ) -> Product:
        """Create product with initial inventory"""
        # Create product first
        product = self.create(db=db, obj_in=product_data)
        
        # Create inventory record
        inventory = Inventory(
            product_id=product.id,
            quantity_on_hand=initial_quantity,
            reorder_level=reorder_level
        )
        db.add(inventory)
        db.commit()
        db.refresh(product)
        
        return product


# Create singleton instance
product_repository = ProductRepository()
