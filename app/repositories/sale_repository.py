from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_
from datetime import datetime, date
from app.repositories.base_repository import BaseRepository
from app.models.sale import Sale, SaleItem
from app.schemas.sale_schema import SaleCreate, SaleUpdate


class SaleRepository(BaseRepository[Sale, SaleCreate, SaleUpdate]):
    """Repository cho Sale operations"""
    
    def __init__(self):
        super().__init__(Sale)
    
    def get_with_details(self, db: Session, *, id: int) -> Optional[Sale]:
        """Get sale with customer, user, and items details"""
        return db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.user),
            joinedload(Sale.items).joinedload(SaleItem.product),
            joinedload(Sale.payments)
        ).filter(Sale.id == id).first()
    
    def get_by_invoice_number(self, db: Session, *, invoice_number: str) -> Optional[Sale]:
        """Get sale by invoice number"""
        return db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).filter(Sale.invoice_number == invoice_number).first()
    
    def get_by_customer(
        self, 
        db: Session, 
        *, 
        customer_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sale]:
        """Get sales by customer"""
        return db.query(Sale).options(
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).filter(Sale.customer_id == customer_id).order_by(
            desc(Sale.sale_date)
        ).offset(skip).limit(limit).all()
    
    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sale]:
        """Get sales by user/staff"""
        return db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).filter(Sale.user_id == user_id).order_by(
            desc(Sale.sale_date)
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(
        self, 
        db: Session, 
        *, 
        start_date: date, 
        end_date: date, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sale]:
        """Get sales within date range"""
        return db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).filter(
            and_(
                func.date(Sale.sale_date) >= start_date,
                func.date(Sale.sale_date) <= end_date
            )
        ).order_by(desc(Sale.sale_date)).offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        db: Session, 
        *, 
        status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sale]:
        """Get sales by status"""
        return db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).filter(Sale.status == status).order_by(
            desc(Sale.sale_date)
        ).offset(skip).limit(limit).all()
    
    def get_unpaid_sales(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sale]:
        """Get unpaid sales"""
        return db.query(Sale).options(
            joinedload(Sale.customer)
        ).filter(Sale.is_paid.is_(False)).order_by(
            desc(Sale.sale_date)
        ).offset(skip).limit(limit).all()
    
    def get_recent_sales(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Sale]:
        """Get recent sales"""
        return db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).order_by(desc(Sale.sale_date)).offset(skip).limit(limit).all()
    
    def get_sales_summary_by_date(
        self, 
        db: Session, 
        *, 
        start_date: date, 
        end_date: date
    ) -> dict:
        """Get sales summary for date range"""
        result = db.query(
            func.count(Sale.id).label('total_sales'),
            func.sum(Sale.final_amount).label('total_revenue'),
            func.avg(Sale.final_amount).label('average_sale'),
        ).filter(
            and_(
                func.date(Sale.sale_date) >= start_date,
                func.date(Sale.sale_date) <= end_date,
                Sale.status == 'completed'
            )
        ).first()
        
        return {
            'total_sales': result.total_sales or 0,
            'total_revenue': float(result.total_revenue or 0),
            'average_sale': float(result.average_sale or 0),
            'start_date': start_date,
            'end_date': end_date
        }


class SaleItemRepository(BaseRepository[SaleItem, dict, dict]):
    """Repository cho SaleItem operations"""
    
    def __init__(self):
        super().__init__(SaleItem)
    
    def get_by_sale_id(self, db: Session, *, sale_id: int) -> List[SaleItem]:
        """Get sale items by sale ID"""
        return db.query(SaleItem).options(
            joinedload(SaleItem.product)
        ).filter(SaleItem.sale_id == sale_id).all()
    
    def get_by_product_id(
        self, 
        db: Session, 
        *, 
        product_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[SaleItem]:
        """Get sale items by product ID"""
        return db.query(SaleItem).options(
            joinedload(SaleItem.sale).joinedload(Sale.customer)
        ).filter(SaleItem.product_id == product_id).order_by(
            desc(SaleItem.id)
        ).offset(skip).limit(limit).all()
    
    def get_top_selling_products(
        self, 
        db: Session, 
        *, 
        start_date: date = None, 
        end_date: date = None, 
        limit: int = 10
    ) -> List[dict]:
        """Get top selling products"""
        query = db.query(
            SaleItem.product_id,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.line_total).label('total_revenue'),
            func.count(SaleItem.id).label('total_orders')
        ).join(Sale)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    func.date(Sale.sale_date) >= start_date,
                    func.date(Sale.sale_date) <= end_date
                )
            )
        
        results = query.filter(Sale.status == 'completed').group_by(
            SaleItem.product_id
        ).order_by(desc('total_quantity')).limit(limit).all()
        
        return [
            {
                'product_id': result.product_id,
                'total_quantity': result.total_quantity,
                'total_revenue': float(result.total_revenue),
                'total_orders': result.total_orders
            }
            for result in results
        ]


# Create singleton instances
sale_repository = SaleRepository()
sale_item_repository = SaleItemRepository()
