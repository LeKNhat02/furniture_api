from sqlalchemy.orm import Session
from app.database.models import Sale, SaleItem, Product, Inventory, Customer
from app.schemas.sale_schema import SaleCreate, SaleUpdate
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

class SaleService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_sale(self, sale_data: SaleCreate, user_id: int = None) -> Sale:
        """Create a new sale"""
        # Validate customer exists
        customer = self.db.query(Customer).filter(Customer.id == sale_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Validate items
        if not sale_data.items or len(sale_data.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sale must have at least one item"
            )
        
        # Calculate totals and validate inventory
        total_amount = 0
        for item in sale_data.items:
            product = self.db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.product_id} not found"
                )
            
            inventory = self.db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            
            if not inventory or inventory.quantity_on_hand < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.name}"
                )
            
            line_total = item.quantity * item.unit_price - item.discount
            total_amount += line_total
        
        # Create sale
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        final_amount = total_amount - sale_data.discount + sale_data.tax
        
        sale = Sale(
            invoice_number=invoice_number,
            customer_id=sale_data.customer_id,
            user_id=user_id,
            total_amount=total_amount,
            discount=sale_data.discount,
            tax=sale_data.tax,
            final_amount=final_amount,
            notes=sale_data.notes
        )
        self.db.add(sale)
        self.db.flush()
        
        # Add items and update inventory
        for item in sale_data.items:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                line_total=item.quantity * item.unit_price - item.discount
            )
            self.db.add(sale_item)
            
            # Update inventory
            inventory = self.db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            inventory.quantity_on_hand -= item.quantity
        
        self.db.commit()
        self.db.refresh(sale)
        return sale
    
    def get_all_sales(self, skip: int = 0, limit: int = 100) -> List[Sale]:
        """Get all sales with pagination"""
        return self.db.query(Sale).offset(skip).limit(limit).all()
    
    def get_sales_count(self) -> int:
        """Get total count of all sales"""
        return self.db.query(Sale).count()
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """Get sale by ID"""
        return self.db.query(Sale).filter(Sale.id == sale_id).first()
    
    def update_sale(self, sale_id: int, sale_data: SaleUpdate) -> Sale:
        """Update sale information"""
        sale = self.get_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        update_dict = sale_data.dict(exclude_unset=True) if hasattr(sale_data, 'dict') else sale_data.__dict__
        for key, value in update_dict.items():
            if value is not None:
                setattr(sale, key, value)
        
        self.db.commit()
        self.db.refresh(sale)
        return sale
    
    def delete_sale(self, sale_id: int):
        """Delete sale and restore inventory"""
        sale = self.get_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        # Restore inventory
        for item in sale.items:
            inventory = self.db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            if inventory:
                inventory.quantity_on_hand += item.quantity
        
        # Delete sale (cascades to items)
        self.db.delete(sale)
        self.db.commit()