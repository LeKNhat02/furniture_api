from app.schemas.user import UserLogin
import hashlib

class UserService:
    def __init__(self, db):
        self.db = db
        self.collection = db.users
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return UserService.hash_password(plain_password) == hashed_password
    
    async def authenticate_user(self, username: str, password: str):
        user = await self.collection.find_one({"username": username})
        if user and self.verify_password(password, user["password_hash"]):
            user["_id"] = str(user["_id"])
            return user
        return None
    
    async def create_demo_users(self):
        admin = await self.collection.find_one({"username": "admin"})
        if not admin:
            await self.collection.insert_many([
                {
                    "username": "admin",
                    "email": "admin@furniture.com",
                    "password_hash": self.hash_password("password123"),
                    "full_name": "Admin User",
                    "role": "admin",
                    "is_active": True
                },
                {
                    "username": "staff",
                    "email": "staff@furniture.com",
                    "password_hash": self.hash_password("password123"),
                    "full_name": "Staff User",
                    "role": "staff",
                    "is_active": True
                }
            ])