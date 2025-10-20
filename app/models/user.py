from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: str
    password_hash: str
    full_name: str
    role: str = "staff"  # admin or staff
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True