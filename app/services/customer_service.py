from bson import ObjectId
from app.schemas.customer import CustomerCreate, CustomerUpdate
from datetime import datetime
from typing import Optional

class CustomerService:
    def __init__(self, db):
        self.db = db
        self.collection = db.customers

    async def get_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        query = {}
        if search:
            query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            }
        
        customers = []
        cursor = self.collection.find(query).skip(skip).limit(limit)
        async for customer in cursor:
            customer["_id"] = str(customer["_id"])
            customers.append(customer)
        return customers

    async def get_total_count(self, search: Optional[str] = None):
        query = {}
        if search:
            query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            }
        return await self.collection.count_documents(query)
    
    async def get_by_id(self, customer_id: str):
        try:
            customer = await self.collection.find_one({"_id": ObjectId(customer_id)})
            if customer:
                customer["_id"] = str(customer["_id"])
            return customer
        except Exception:
            return None
        
    async def create(self, customer_data: CustomerCreate):
        customer_dict = customer_data.model_dump()
        customer_dict["total_spent"] = 0.0
        customer_dict["total_orders"] = 0
        customer_dict["created_at"] = datetime.utcnow()
        customer_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(customer_dict)
        customer_dict["_id"] = str(result.inserted_id)
        return customer_dict
    
    async def update(self, customer_id: str, customer: CustomerUpdate):
        try:
            update_dict = customer.model_dump()
            update_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_dict}
            )

            if result.matched_count:
                updated = await self.get_by_id(customer_id)
                return updated
            return None
        except Exception:
            return None
        
    async def delete(self, customer_id: str):
        try:
            result = await self.collection.delete_one({"_id": ObjectId(customer_id)})
            return result.deleted_count > 0
        except Exception: 
            return False

    async def update_customer_stats(self, customer_id: str, order_amount: float):
        """Cập nhật thống kê khách hàng sau khi có đơn hàng mới"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {
                    "$inc": {"total_spent": order_amount, "total_orders": 1},
                    "$set": {"last_order_date": datetime.utcnow()}
                }
            )
        except Exception:
            pass