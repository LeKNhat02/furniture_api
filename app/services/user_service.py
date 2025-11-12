from sqlalchemy.orm import Session
from app.repositories import user_repository
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from fastapi import HTTPException, status
from typing import List, Optional

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserResponse:
        """Create new user using repository"""
        return user_repository.create(db=db, obj_in=user_data)
    
    @staticmethod
    def get_all_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[UserResponse]:
        """Get all users with optional search"""
        if search:
            return user_repository.search_users(db=db, search=search, skip=skip, limit=limit)
        else:
            return user_repository.get_multi(db=db, skip=skip, limit=limit)
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> UserResponse:
        """Get user by ID"""
        user = user_repository.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> UserResponse:
        """Get user by username"""
        user = user_repository.get_by_username(db=db, username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> UserResponse:
        """Get user by email"""
        user = user_repository.get_by_email(db=db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update user using repository"""
        updated_user = user_repository.update(db=db, db_obj_id=user_id, obj_in=user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        """Delete user using repository"""
        success = user_repository.remove(db=db, id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deleted successfully"}
    
    @staticmethod
    def get_users_by_role(
        db: Session, 
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserResponse]:
        """Get users by role"""
        return user_repository.get_by_role(db=db, role=role, skip=skip, limit=limit)
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> UserResponse:
        """Activate user account"""
        user = user_repository.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Assuming we have an is_active field (update based on your User model)
        updated_data = UserUpdate(is_active=True)
        return user_repository.update(db=db, db_obj_id=user_id, obj_in=updated_data)
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> UserResponse:
        """Deactivate user account"""
        user = user_repository.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Assuming we have an is_active field (update based on your User model)
        updated_data = UserUpdate(is_active=False)
        return user_repository.update(db=db, db_obj_id=user_id, obj_in=updated_data)
    
    @staticmethod
    def get_user_statistics(db: Session) -> dict:
        """Get user statistics"""
        total_users = user_repository.count_all(db=db)
        admin_count = len(user_repository.get_by_role(db=db, role="admin", limit=1000))
        staff_count = len(user_repository.get_by_role(db=db, role="staff", limit=1000))
        
        return {
            "total_users": total_users,
            "admin_users": admin_count,
            "staff_users": staff_count
        }
