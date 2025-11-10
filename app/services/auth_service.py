from sqlalchemy.orm import Session
from app.database.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user_schema import UserCreate, UserLogin
from fastapi import HTTPException, status

class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate):
        user = db.query(User).filter(User.username == user_data.username).first()
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
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def login_user(db: Session, user_data: UserLogin):
        user = db.query(User).filter(User.username == user_data.username).first()
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