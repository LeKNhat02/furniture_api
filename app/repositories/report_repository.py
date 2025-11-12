from typing import List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.report import Report


class ReportRepository(BaseRepository[Report, dict, dict]):
    """Repository cho Report operations"""
    
    def __init__(self):
        super().__init__(Report)
    
    def get_by_type(
        self, 
        db: Session, 
        *, 
        report_type: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """Get reports by type"""
        return db.query(Report).filter(
            Report.report_type == report_type
        ).offset(skip).limit(limit).all()
    
    def get_by_generated_by(
        self, 
        db: Session, 
        *, 
        generated_by: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """Get reports by who generated them"""
        return db.query(Report).filter(
            Report.generated_by == generated_by
        ).offset(skip).limit(limit).all()


# Create singleton instance
report_repository = ReportRepository()
