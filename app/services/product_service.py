from bson import ObjectId
from app.schemas.product import ProductCreate, ProductUpdate
from datetime import datetime
from typing import Optional

class ProductService:
    def __init__(self, db):
        self.db = db
        self.collection = db.products

    async def get_all(self, skip: int = 0, limit: int = 100, 
                     search: Optional[str] = None, 
                     category: Optional[str] = None,
                     is_active: Optional[bool] = True):
        query = {}
        
        if is_active is not None:
            query["is_active"] = is_active
            
        if category:
            query["category"] = category
            
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"sku": {"$regex": search, "$options": "i"}}
            ]
        
        products = []
        cursor = self.collection.find(query).skip(skip).limit(limit)
        async for product in cursor:
            product["_id"] = str(product["_id"])
            products.append(product)
        return products

    async def get_total_count(self, search: Optional[str] = None, 
                             category: Optional[str] = None,
                             is_active: Optional[bool] = True):
        query = {}
        
        if is_active is not None:
            query["is_active"] = is_active
            
        if category:
            query["category"] = category
            
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"sku": {"$regex": search, "$options": "i"}}
            ]
            
        return await self.collection.count_documents(query)
    
    async def get_by_id(self, product_id: str):
        try:
            product = await self.collection.find_one({"_id": ObjectId(product_id)})
            if product:
                product["_id"] = str(product["_id"])
            return product
        except Exception:
            return None
        
    async def create(self, product_data: ProductCreate):
        product_dict = product_data.model_dump()
        product_dict["created_at"] = datetime.utcnow()
        product_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(product_dict)
        product_dict["_id"] = str(result.inserted_id)
        return product_dict
    
    async def update(self, product_id: str, product: ProductUpdate):
        try:
            update_dict = product.model_dump()
            update_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_dict}
            )

            if result.matched_count:
                updated = await self.get_by_id(product_id)
                return updated
            return None
        except Exception:
            return None
        
    async def delete(self, product_id: str):
        try:
            result = await self.collection.delete_one({"_id": ObjectId(product_id)})
            return result.deleted_count > 0
        except Exception: 
            return False

