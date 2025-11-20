from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.report_schema import (
    RevenueReportItem, TopProductItem, CustomerReportItem,
    InventoryReportItem, DashboardSummary
)
from app.services.report_service import ReportService
from app.core.security import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard summary"""
    try:
        service = ReportService(db)
        summary = service.get_dashboard_summary()
        return {
            "data": summary,
            "message": "Dashboard summary retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue")
async def revenue_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get revenue report for last N days"""
    try:
        service = ReportService(db)
        report = service.get_revenue_report(days)
        return {
            "data": report,
            "message": "Revenue report retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving revenue report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-products")
async def top_products_report(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get top selling products"""
    try:
        service = ReportService(db)
        report = service.get_top_products(limit)
        return {
            "data": report,
            "message": "Top products report retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving top products report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers")
async def customer_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get customer purchase report"""
    try:
        service = ReportService(db)
        report = service.get_customer_report()
        return {
            "data": report,
            "message": "Customer report retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving customer report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory")
async def inventory_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory status report"""
    try:
        service = ReportService(db)
        report = service.get_inventory_report()
        return {
            "data": report,
            "message": "Inventory report retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving inventory report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))