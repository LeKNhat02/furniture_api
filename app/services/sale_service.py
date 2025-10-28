from bson import ObjectId
from app.schemas.sale import SaleCreate, SaleUpdate
from datetime import datetime
from typing import Optional
import uuid

class SaleService:
    def __init__(self, db):
        self.db = db
        self.collection = db.sales

    def generate_sale_number(self):
        """Tạo mã đơn hàng duy nhất"""
        now = datetime.utcnow()
        return f"ORD{now.strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

    async def get_all(self, skip: int = 0, limit: int = 100, 
                     start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None,
                     customer_id: Optional[str] = None,
                     payment_status: Optional[str] = None):
        query = {}
        
        if start_date and end_date:
            query["sale_date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["sale_date"] = {"$gte": start_date}
        elif end_date:
            query["sale_date"] = {"$lte": end_date}
            
        if customer_id:
            query["customer_id"] = customer_id
            
        if payment_status:
            query["payment_status"] = payment_status
        
        sales = []
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        async for sale in cursor:
            sale["_id"] = str(sale["_id"])
            sales.append(sale)
        return sales

    async def get_total_count(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None,
                             customer_id: Optional[str] = None,
                             payment_status: Optional[str] = None):
        query = {}
        
        if start_date and end_date:
            query["sale_date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["sale_date"] = {"$gte": start_date}
        elif end_date:
            query["sale_date"] = {"$lte": end_date}
            
        if customer_id:
            query["customer_id"] = customer_id
            
        if payment_status:
            query["payment_status"] = payment_status
            
        return await self.collection.count_documents(query)
    
    async def get_by_id(self, sale_id: str):
        try:
            sale = await self.collection.find_one({"_id": ObjectId(sale_id)})
            if sale:
                sale["_id"] = str(sale["_id"])
            return sale
        except Exception:
            return None
        
    async def create(self, sale_data: SaleCreate, created_by: str):
        sale_dict = sale_data.model_dump()
        sale_dict["sale_number"] = self.generate_sale_number()
        sale_dict["payment_status"] = "pending"
        sale_dict["created_by"] = created_by
        sale_dict["sale_date"] = datetime.utcnow()
        sale_dict["created_at"] = datetime.utcnow()
        sale_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(sale_dict)
        sale_dict["_id"] = str(result.inserted_id)
        
        # Cập nhật inventory
        await self._update_inventory_after_sale(sale_dict["items"])
        
        return sale_dict
    
    async def update(self, sale_id: str, sale: SaleUpdate):
        try:
            update_dict = sale.model_dump(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.update_one(
                {"_id": ObjectId(sale_id)},
                {"$set": update_dict}
            )

            if result.matched_count:
                updated = await self.get_by_id(sale_id)
                return updated
            return None
        except Exception:
            return None
        
    async def delete(self, sale_id: str):
        try:
            # Lấy thông tin sale trước khi xóa để hoàn trả inventory
            sale = await self.get_by_id(sale_id)
            if sale:
                await self._restore_inventory_after_delete(sale["items"])
                
            result = await self.collection.delete_one({"_id": ObjectId(sale_id)})
            return result.deleted_count > 0
        except Exception: 
            return False

    async def _update_inventory_after_sale(self, items):
        """Cập nhật tồn kho sau khi bán"""
        for item in items:
            try:
                await self.db.products.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {"$inc": {"quantity": -item["quantity"]}}
                )
                
                # Ghi lại movement
                movement = {
                    "product_id": item["product_id"],
                    "movement_type": "export",
                    "quantity": -item["quantity"],
                    "reason": "sale",
                    "created_at": datetime.utcnow()
                }
                await self.db.inventory_movements.insert_one(movement)
            except Exception:
                continue

    async def _restore_inventory_after_delete(self, items):
        """Hoàn trả tồn kho khi xóa đơn hàng"""
        for item in items:
            try:
                await self.db.products.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {"$inc": {"quantity": item["quantity"]}}
                )
                
                # Ghi lại movement
                movement = {
                    "product_id": item["product_id"],
                    "movement_type": "import",
                    "quantity": item["quantity"],
                    "reason": "return",
                    "created_at": datetime.utcnow()
                }
                await self.db.inventory_movements.insert_one(movement)
            except Exception:
                continue