from fastapi import APIRouter, Query
from app.database.db import get_database
from app.services.report_service import ReportService
from datetime import datetime, timedelta

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/dashboard", response_model=dict)
async def get_dashboard_stats():
    """Thống kê tổng quan cho dashboard"""
    db = get_database()
    service = ReportService(db)
    return await service.get_dashboard_stats()

@router.get("/revenue", response_model=list)
async def get_revenue_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    group_by: str = Query("day", regex="^(day|month|year)$")
):
    """Báo cáo doanh thu theo thời gian"""
    db = get_database()
    service = ReportService(db)
    return await service.get_revenue_report(start_date, end_date, group_by)

@router.get("/top-products", response_model=list)
async def get_top_products(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Top sản phẩm bán chạy"""
    db = get_database()
    service = ReportService(db)
    
    # Mặc định lấy dữ liệu tháng hiện tại
    if not start_date or not end_date:
        now = datetime.utcnow()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    return await service.get_top_products(start_date, end_date, limit)

@router.get("/customers", response_model=list)
async def get_customer_report(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None)
):
    """Báo cáo khách hàng"""
    db = get_database()
    service = ReportService(db)
    
    # Mặc định lấy dữ liệu tháng hiện tại
    if not start_date or not end_date:
        now = datetime.utcnow()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    return await service.get_customer_report(start_date, end_date)

@router.get("/inventory", response_model=list)
async def get_inventory_report():
    """Báo cáo tồn kho"""
    db = get_database()
    service = ReportService(db)
    return await service.get_inventory_report()