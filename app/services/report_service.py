from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database.models import (
    Sale, Product, SaleItem, Customer, Inventory, InventoryTransaction
)
from app.schemas.report_schema import (
    RevenueReportItem, TopProductItem, CustomerReportItem, 
    InventoryReportItem, DashboardSummary
)
from datetime import datetime, timedelta
from typing import List

class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_revenue_report(self, days: int = 30) -> List[RevenueReportItem]:
        """Get revenue report for last N days"""
        start_date = datetime.now() - timedelta(days=days)
        
        revenue = self.db.query(
            func.date(Sale.sale_date).label('date'),
            func.sum(Sale.final_amount).label('total')
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            func.date(Sale.sale_date)
        ).order_by(
            func.date(Sale.sale_date)
        ).all()
        
        return [
            RevenueReportItem(date=r[0], total=r[1] or 0)
            for r in revenue
        ]
    
    def get_top_products(self, limit: int = 10) -> List[TopProductItem]:
        """Get top selling products"""
        top_products = self.db.query(
            Product.id,
            Product.name,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.line_total).label('total_sales')
        ).join(
            SaleItem, Product.id == SaleItem.product_id
        ).group_by(
            Product.id, Product.name
        ).order_by(
            func.sum(SaleItem.quantity).desc()
        ).limit(limit).all()
        
        return [
            TopProductItem(
                product_id=p[0],
                product_name=p[1],
                total_quantity=p[2] or 0,
                total_sales=p[3] or 0
            )
            for p in top_products
        ]
    
    def get_customer_report(self) -> List[CustomerReportItem]:
        """Get customer purchase report"""
        customers = self.db.query(
            Customer.id,
            Customer.name,
            func.count(Sale.id).label('total_purchases'),
            func.sum(Sale.final_amount).label('total_spent')
        ).join(
            Sale, Customer.id == Sale.customer_id
        ).group_by(
            Customer.id, Customer.name
        ).order_by(
            func.sum(Sale.final_amount).desc()
        ).all()
        
        return [
            CustomerReportItem(
                customer_id=c[0],
                customer_name=c[1],
                total_purchases=c[2] or 0,
                total_spent=c[3] or 0
            )
            for c in customers
        ]
    
    def get_inventory_report(self) -> List[InventoryReportItem]:
        """Get inventory status report"""
        inventory_items = self.db.query(Inventory).all()
        
        result = []
        for inv in inventory_items:
            if inv.quantity_on_hand <= 0:
                status = "CRITICAL"
            elif inv.quantity_on_hand <= inv.reorder_level:
                status = "LOW"
            else:
                status = "OK"
            
            result.append(InventoryReportItem(
                product_id=inv.product_id,
                product_name=inv.product.name,
                quantity_on_hand=inv.quantity_on_hand,
                quantity_reserved=inv.quantity_reserved,
                reorder_level=inv.reorder_level,
                status=status
            ))
        
        return result
    
    def get_dashboard_summary(self) -> DashboardSummary:
        """Get dashboard summary"""
        today = datetime.now().date()
        
        # Total sales and revenue
        total_sales = self.db.query(func.sum(Sale.final_amount)).scalar() or 0
        total_sales_count = self.db.query(func.count(Sale.id)).scalar() or 0
        
        # Today's sales
        today_sales = self.db.query(func.sum(Sale.final_amount)).filter(
            func.date(Sale.sale_date) == today
        ).scalar() or 0
        today_sales_count = self.db.query(func.count(Sale.id)).filter(
            func.date(Sale.sale_date) == today
        ).scalar() or 0
        
        # Total customers
        total_customers = self.db.query(func.count(Customer.id)).scalar() or 0
        
        # Total products
        total_products = self.db.query(func.count(Product.id)).filter(
            Product.is_active == True
        ).scalar() or 0
        
        # Low stock count
        low_stock_count = self.db.query(func.count(Inventory.id)).filter(
            Inventory.quantity_on_hand <= Inventory.reorder_level
        ).scalar() or 0
        
        return DashboardSummary(
            total_sales=total_sales_count,
            total_revenue=total_sales,
            total_customers=total_customers,
            total_products=total_products,
            low_stock_count=low_stock_count,
            today_sales=today_sales,
            today_sales_count=today_sales_count
        )