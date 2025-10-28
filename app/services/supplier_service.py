from bson import ObjectId
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from datetime import datetime
from typing import Optional

class SupplierService:
    def __init__(self, db):
        self.db = db
        self.collection = db.suppliers

    async def get_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        query = {}
        if search:
            query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"contact_person": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            }
        
        suppliers = []
        cursor = self.collection.find(query).skip(skip).limit(limit)
        async for supplier in cursor:
            supplier["_id"] = str(supplier["_id"])
            suppliers.append(supplier)
        return suppliers

    async def get_total_count(self, search: Optional[str] = None):
        query = {}
        if search:
            query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"contact_person": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            }
        return await self.collection.count_documents(query)
    
    async def get_by_id(self, supplier_id: str):
        try:
            supplier = await self.collection.find_one({"_id": ObjectId(supplier_id)})
            if supplier:
                supplier["_id"] = str(supplier["_id"])
            return supplier
        except Exception:
            return None
        
    async def create(self, supplier_data: SupplierCreate):
        supplier_dict = supplier_data.model_dump()
        supplier_dict["created_at"] = datetime.utcnow()
        supplier_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(supplier_dict)
        supplier_dict["_id"] = str(result.inserted_id)
        return supplier_dict
    
    async def update(self, supplier_id: str, supplier: SupplierUpdate):
        try:
            update_dict = supplier.model_dump()
            update_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.update_one(
                {"_id": ObjectId(supplier_id)},
                {"$set": update_dict}
            )

            if result.matched_count:
                updated = await self.get_by_id(supplier_id)
                return updated
            return None
        except Exception:
            return None
        
    async def delete(self, supplier_id: str):
        try:
            result = await self.collection.delete_one({"_id": ObjectId(supplier_id)})
            return result.deleted_count > 0
        except Exception: 
            return False