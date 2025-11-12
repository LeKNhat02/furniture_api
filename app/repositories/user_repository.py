from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository cho User operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100):
        """Get all active users"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_by_role(self, db: Session, *, role: str, skip: int = 0, limit: int = 100):
        """Get users by role"""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    def search_users(self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100):
        """Search users by username, email, or full_name"""
        return self.search(
            db=db,
            search_term=search_term,
            search_fields=["username", "email", "full_name"],
            skip=skip,
            limit=limit
        )


# Create singleton instance
user_repository = UserRepository()
