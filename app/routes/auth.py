from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.user_schema import (
    UserCreate, UserLogin, TokenResponse, UserResponse, 
    ChangePasswordRequest, UpdateProfileRequest
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.database.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        service = AuthService(db)
        user = service.register_user(user_data)
        return {
            "data": user,
            "message": "User registered successfully",
            "status_code": 201
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and get token"""
    try:
        service = AuthService(db)
        token = service.login_user(user_data)
        return {
            "data": token,
            "message": "Login successful",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    try:
        return {
            "data": current_user,
            "message": "User profile retrieved successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout endpoint - client should delete token from storage"""
    try:
        return {
            "data": None,
            "message": "Logged out successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        service = AuthService(db)
        result = service.change_password(current_user, request)
        return {
            "data": result,
            "message": "Password changed successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        service = AuthService(db)
        user = service.update_profile(current_user, request)
        return {
            "data": user,
            "message": "Profile updated successfully",
            "status_code": 200
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))