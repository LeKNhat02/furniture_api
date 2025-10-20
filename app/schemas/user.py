from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str

    class Config:
        populate_by_name = True

class LoginResponse(BaseModel):
    access_token: str
    user: UserResponse