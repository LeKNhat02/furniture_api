from sqlalchemy.orm import Session
from app.repositories import user_repository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user_schema import (
    UserCreate, UserLogin, ChangePasswordRequest, 
    UserUpdate, UserResponse
)
from fastapi import HTTPException, status

class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate):
        # Check if user exists using repository
        existing_user = user_repository.get_by_username(db=db, username=user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create user using repository
        new_user = user_repository.create(db=db, obj_in=user_data)
        return new_user
    
    @staticmethod
    def login_user(db: Session, user_data: UserLogin):
        # Get user by username using repository
        user = user_repository.get_by_username(db=db, username=user_data.username)
        
        # Verify user and password
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token = create_access_token(data={"sub": user.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    @staticmethod
    def logout_user():
        """Logout user - client side token removal"""
        return {"message": "Logged out successfully"}
    
    @staticmethod
    def change_password(db: Session, user_id: int, password_data: ChangePasswordRequest):
        """Change user password"""
        # Get current user using repository
        user = user_repository.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not verify_password(password_data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect"
            )
        
        # Update password using repository
        hashed_new_password = hash_password(password_data.new_password)
        updated_data = UserUpdate(hashed_password=hashed_new_password)
        user_repository.update(db=db, db_obj_id=user_id, obj_in=updated_data)
        
        return {"message": "Password changed successfully"}
    
    @staticmethod
    def update_profile(db: Session, user_id: int, user_data: UserUpdate):
        """Update user profile"""
        # Get current user using repository
        user = user_repository.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email conflict if email is being updated
        if user_data.email and user_data.email != user.email:
            existing = user_repository.get_by_email(db=db, email=user_data.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Update user using repository
        updated_user = user_repository.update(db=db, db_obj_id=user_id, obj_in=user_data)
        return updated_user
    
    @staticmethod
    def forgot_password(db: Session, email: str):
        """Request password reset - placeholder for email service"""
        user = user_repository.get_by_email(db=db, email=email)
        if not user:
            # Không tiết lộ email có tồn tại hay không
            return {"message": "If email exists, password reset link has been sent"}
        
        # TODO: Implement email service to send reset token
        # For now, just return success message
        return {"message": "If email exists, password reset link has been sent"}
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str):
        """Reset password with token - placeholder"""
        # TODO: Implement token validation and reset logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Password reset not implemented yet"
        )
    
    @staticmethod
    def verify_email(db: Session, token: str):
        """Verify email with token - placeholder"""
        # TODO: Implement email verification logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Email verification not implemented yet"
        )
    
    @staticmethod
    def resend_verification(db: Session, email: str):
        """Resend verification email - placeholder"""
        # TODO: Implement resend verification logic
        return {"message": "If email exists, verification link has been sent"}