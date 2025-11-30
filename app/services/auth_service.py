from sqlalchemy.orm import Session
from app.database.models import User, Customer
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user_schema import UserCreate, UserLogin, ChangePasswordRequest, UpdateProfileRequest
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate):
        user = self.db.query(User).filter(User.username == user_data.username).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            role=user_data.role
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Tự động tạo Customer nếu role là customer/user
        if user_data.role in ['customer', 'user']:
            new_customer = Customer(
                user_id=new_user.id,
                name=user_data.full_name or user_data.username,
                email=user_data.email,
                phone=user_data.phone,
                address=None,
                city=None,
                country='Việt Nam'
            )
            self.db.add(new_customer)
            self.db.commit()
        
        return new_user
    
    def login_user(self, user_data: UserLogin):
        user = self.db.query(User).filter(User.username == user_data.username).first()
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
    
    def change_password(self, current_user: User, request: ChangePasswordRequest):
        # Verify old password
        if not verify_password(request.old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Old password is incorrect"
            )
        
        # Validate new passwords match
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )
        
        # Validate new password is different from old
        if request.old_password == request.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from old password"
            )
        
        # Update password
        current_user.hashed_password = hash_password(request.new_password)
        self.db.commit()
        self.db.refresh(current_user)
        
        return {"message": "Password changed successfully"}
    
    def update_profile(self, current_user: User, request: UpdateProfileRequest):
        # Check email uniqueness if email is being changed
        if request.email and request.email != current_user.email:
            existing_user = self.db.query(User).filter(User.email == request.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            current_user.email = request.email
        
        if request.full_name:
            current_user.full_name = request.full_name
        
        if request.phone:
            current_user.phone = request.phone
        
        self.db.commit()
        self.db.refresh(current_user)
        return current_user