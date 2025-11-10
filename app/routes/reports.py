from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.report_schema import (
    RevenueReportItem, TopProductItem, CustomerReportItem,
    InventoryReportItem, DashboardSummary
)
from app.services.report_service import ReportService
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard summary"""
    return ReportService.get_dashboard_summary(db)

@router.get("/revenue", response_model=List[RevenueReportItem])
def revenue_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get revenue report for last N days"""
    return ReportService.get_revenue_report(db, days)

@router.get("/top-products", response_model=List[TopProductItem])
def top_products_report(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get top selling products"""
    return ReportService.get_top_products(db, limit)

@router.get("/customers", response_model=List[CustomerReportItem])
def customer_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get customer purchase report"""
    return ReportService.get_customer_report(db)

@router.get("/inventory", response_model=List[InventoryReportItem])
def inventory_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory status report"""
    return ReportService.get_inventory_report(db)