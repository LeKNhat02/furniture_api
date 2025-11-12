from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.user_schema import (
    UserCreate, UserLogin, TokenResponse, UserResponse,
    ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest,
    RefreshTokenRequest, VerifyEmailRequest, UserUpdate
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login_user(db, user_data)

@router.post("/logout")
def logout(current_user = Depends(get_current_user)):
    """Logout user"""
    return AuthService.logout_user()

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Change user password"""
    return AuthService.change_password(db, current_user, password_data)

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    return AuthService.forgot_password(db, request.email)

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    return AuthService.reset_password(db, request.token, request.new_password)

@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest):
    """Refresh access token - placeholder"""
    # TODO: Implement refresh token logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token not implemented yet"
    )

@router.post("/verify-email")
def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Verify email with token"""
    return AuthService.verify_email(db, request.token)

@router.post("/resend-verification")
def resend_verification(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Resend verification email"""
    return AuthService.resend_verification(db, request.email)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update user profile"""
    return AuthService.update_profile(db, current_user, user_data)