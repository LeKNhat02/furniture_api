from bson import ObjectId
from app.schemas.promotion import PromotionCreate, PromotionUpdate
from datetime import datetime
from typing import Optional

class PromotionService:
    def __init__(self, db):
        self.db = db
        self.collection = db.promotions

    async def get_all(self, skip: int = 0, limit: int = 100, 
                     is_active: Optional[bool] = None,
                     current_only: bool = False):
        query = {}
        
        if is_active is not None:
            query["is_active"] = is_active
            
        if current_only:
            now = datetime.utcnow()
            query["start_date"] = {"$lte": now}
            query["end_date"] = {"$gte": now}
        
        promotions = []
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        async for promotion in cursor:
            promotion["_id"] = str(promotion["_id"])
            promotions.append(promotion)
        return promotions

    async def get_total_count(self, is_active: Optional[bool] = None, current_only: bool = False):
        query = {}
        
        if is_active is not None:
            query["is_active"] = is_active
            
        if current_only:
            now = datetime.utcnow()
            query["start_date"] = {"$lte": now}
            query["end_date"] = {"$gte": now}
            
        return await self.collection.count_documents(query)
    
    async def get_by_id(self, promotion_id: str):
        try:
            promotion = await self.collection.find_one({"_id": ObjectId(promotion_id)})
            if promotion:
                promotion["_id"] = str(promotion["_id"])
            return promotion
        except Exception:
            return None
        
    async def create(self, promotion_data: PromotionCreate):
        promotion_dict = promotion_data.model_dump()
        promotion_dict["used_count"] = 0
        promotion_dict["created_at"] = datetime.utcnow()
        promotion_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(promotion_dict)
        promotion_dict["_id"] = str(result.inserted_id)
        return promotion_dict
    
    async def update(self, promotion_id: str, promotion: PromotionUpdate):
        try:
            update_dict = promotion.model_dump()
            update_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.update_one(
                {"_id": ObjectId(promotion_id)},
                {"$set": update_dict}
            )

            if result.matched_count:
                updated = await self.get_by_id(promotion_id)
                return updated
            return None
        except Exception:
            return None
        
    async def delete(self, promotion_id: str):
        try:
            result = await self.collection.delete_one({"_id": ObjectId(promotion_id)})
            return result.deleted_count > 0
        except Exception: 
            return False

    async def get_applicable_promotions(self, order_amount: float, product_ids: list = None):
        """Lấy các khuyến mãi có thể áp dụng cho đơn hàng"""
        now = datetime.utcnow()
        query = {
            "is_active": True,
            "start_date": {"$lte": now},
            "end_date": {"$gte": now},
            "$or": [
                {"min_order_amount": {"$lte": order_amount}},
                {"min_order_amount": {"$exists": False}}
            ]
        }
        
        promotions = []
        async for promotion in self.collection.find(query):
            promotion["_id"] = str(promotion["_id"])
            
            # Kiểm tra giới hạn sử dụng
            if promotion.get("usage_limit") and promotion.get("used_count", 0) >= promotion["usage_limit"]:
                continue
                
            # Kiểm tra sản phẩm áp dụng
            if promotion.get("applicable_products") and product_ids:
                if not any(pid in promotion["applicable_products"] for pid in product_ids):
                    continue
                    
            promotions.append(promotion)
            
        return promotions

    async def use_promotion(self, promotion_id: str):
        """Tăng số lần sử dụng promotion"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(promotion_id)},
                {"$inc": {"used_count": 1}}
            )
        except Exception:
            pass