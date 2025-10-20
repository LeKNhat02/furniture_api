from bson import ObjectId
from app.schemas.product import ProductCreate, ProductUpdate
from datetime import datetime

class ProductService:
    def __init__(self, db):
        self.db = db
        self.collection = db.products

        async def get_all(self):
            product = []
            async for product in self.collection.find():
                product["_id"] = str(product["_id"])
                product.append(product)
            return product
        
        async def get_by_id(self, product_id: str):
            try:
                product = await self.collection.find_one({"_id": ObjectId(product_id)})
                if product:
                    product["_id"] = str(product["_id"])
                return product
            except Exception:
                return None
            
        async def create(self, product_data: ProductCreate):
            product_dict = product_model_dump()
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
                    update = await self.get_by_id(product_id)
                    return update
                return None
            except:
                return None
            
        async def delete(self, product_id: str):
            try:
                result = await self.collection.delete_one({"_id": ObjectId(product_id)})
                return result.deleted_count > 0
            except: 
                return False

