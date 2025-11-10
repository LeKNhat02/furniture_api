from sqlalchemy.orm import Session
from app.database.models import Sale, SaleItem, Product, Inventory, Customer
from app.schemas.sale_schema import SaleCreate, SaleUpdate
from fastapi import HTTPException, status
from datetime import datetime
from typing import List

class SaleService:
    @staticmethod
    def create_sale(db: Session, sale_data: SaleCreate, user_id: int = None) -> Sale:
        # Validate customer exists
        customer = db.query(Customer).filter(Customer.id == sale_data.customer_id).first()
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
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.product_id} not found"
                )
            
            inventory = db.query(Inventory).filter(
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
        db.add(sale)
        db.flush()
        
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
            db.add(sale_item)
            
            # Update inventory
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            inventory.quantity_on_hand -= item.quantity
        
        db.commit()
        db.refresh(sale)
        return sale
    
    @staticmethod
    def get_all_sales(db: Session, skip: int = 0, limit: int = 100) -> List[Sale]:
        return db.query(Sale).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_sale_by_id(db: Session, sale_id: int) -> Sale:
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        return sale
    
    @staticmethod
    def update_sale(
        db: Session,
        sale_id: int,
        sale_data: SaleUpdate
    ) -> Sale:
        sale = SaleService.get_sale_by_id(db, sale_id)
        
        for key, value in sale_data.dict(exclude_unset=True).items():
            setattr(sale, key, value)
        
        db.commit()
        db.refresh(sale)
        return sale
    
    @staticmethod
    def delete_sale(db: Session, sale_id: int):
        sale = SaleService.get_sale_by_id(db, sale_id)
        
        # Restore inventory
        for item in sale.items:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            if inventory:
                inventory.quantity_on_hand += item.quantity
        
        # Delete sale (cascades to items)
        db.delete(sale)
        db.commit()