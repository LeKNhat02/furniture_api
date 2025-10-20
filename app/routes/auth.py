from fastapi import APIRouter, Depends, HTTPException
from app.database.db import get_database
from app.schemas.user import UserLogin, LoginResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin):
    db = get_database()
    user_service = UserService(db)
    
    user = await user_service.authenticate_user(
        credentials.username,
        credentials.password
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": f"token-{user['_id']}",
        "user": {
            "id": user["_id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }