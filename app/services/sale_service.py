from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.database.models import Sale, SaleItem, Product, Inventory, Customer
from app.schemas.sale_schema import SaleCreate, SaleUpdate, SaleResponse, SaleItemResponse
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional

class SaleService:
    @staticmethod
    def create_sale(db: Session, sale_data: SaleCreate, user_id: int = None):
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
            payment_method=sale_data.payment_method,
            is_paid=sale_data.is_paid,
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
        
        # Return transformed response
        return SaleService._transform_sale_response(db, sale)
    
    @staticmethod
    def get_all_sales(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        # Use joinedload to eagerly load related data
        query = db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        )
        
        if search:
            query = query.join(Customer).filter(
                or_(
                    Sale.invoice_number.contains(search),
                    Customer.name.contains(search),
                    Customer.phone.contains(search)
                )
            )
        
        if status_filter:
            query = query.filter(Sale.status == status_filter)
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
        
        sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
        
        # Transform all sales for frontend compatibility
        result = []
        for sale in sales:
            result.append(SaleService._transform_sale_response(db, sale))
        
        return result
    
    @staticmethod
    def get_sale_by_id(db: Session, sale_id: int):
        sale = db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).filter(Sale.id == sale_id).first()
        
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        return SaleService._transform_sale_response(db, sale)
    
    @staticmethod
    def update_sale(
        db: Session,
        sale_id: int,
        sale_data: SaleUpdate
    ):
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        for key, value in sale_data.dict(exclude_unset=True).items():
            setattr(sale, key, value)
        
        db.commit()
        db.refresh(sale)
        
        return SaleService._transform_sale_response(db, sale)
    
    @staticmethod
    def cancel_sale(db: Session, sale_id: int):
        """Cancel a sale and restore inventory"""
        sale = db.query(Sale).options(joinedload(Sale.items)).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        if sale.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sale is already cancelled"
            )
        
        # Restore inventory
        for item in sale.items:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            if inventory:
                inventory.quantity_on_hand += item.quantity
        
        sale.status = "cancelled"
        db.commit()
        db.refresh(sale)
        
        return SaleService._transform_sale_response(db, sale)
    
    @staticmethod
    def delete_sale(db: Session, sale_id: int):
        sale = db.query(Sale).options(joinedload(Sale.items)).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
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
        return {"message": "Sale deleted successfully"}
    
    @staticmethod
    def _transform_sale_response(db: Session, sale: Sale):
        """Transform sale to match frontend SaleModel expectations"""
        
        # Transform sale items with computed fields
        items = []
        for item in sale.items:
            product = item.product
            item_subtotal = item.unit_price * item.quantity
            subtotal_after_discount = item_subtotal - item.discount
            
            items.append(SaleItemResponse(
                productId=str(item.product_id),  # String for frontend
                productName=product.name if product else '',
                quantity=item.quantity,
                price=item.unit_price,  # Match frontend field name
                discount=item.discount,
                itemSubtotal=item_subtotal,
                subtotal=subtotal_after_discount
            ))
        
        # Calculate totals
        total_subtotal = sum(item.itemSubtotal for item in items)
        total_discount = sum(item.discount for item in items)
        final_total = total_subtotal - total_discount
        total_item_count = sum(item.quantity for item in items)
        
        # Get customer info
        customer = sale.customer
        
        return SaleResponse(
            id=str(sale.id),  # String for frontend compatibility
            orderNumber=sale.invoice_number,  # camelCase
            customerId=str(sale.customer_id) if sale.customer_id else None,  # String type
            customerName=customer.name if customer else None,
            customerPhone=customer.phone if customer else None,
            items=items,  # Embedded items with computed fields
            paymentMethod=sale.payment_method,  # camelCase
            status=sale.status,
            isPaid=sale.is_paid,  # camelCase
            notes=sale.notes,
            createdAt=sale.created_at,  # camelCase
            updatedAt=sale.updated_at,  # camelCase
            subtotal=total_subtotal,
            totalDiscount=total_discount,
            total=final_total,
            itemCount=total_item_count
        )