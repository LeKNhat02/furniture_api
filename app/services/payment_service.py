from bson import ObjectId
from app.schemas.payment import PaymentCreate
from datetime import datetime
from typing import Optional

class PaymentService:
    def __init__(self, db):
        self.db = db
        self.collection = db.payments

    async def get_all(self, skip: int = 0, limit: int = 100, 
                     sale_id: Optional[str] = None,
                     payment_method: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None):
        query = {}
        
        if sale_id:
            query["sale_id"] = sale_id
            
        if payment_method:
            query["payment_method"] = payment_method
            
        if start_date and end_date:
            query["payment_date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["payment_date"] = {"$gte": start_date}
        elif end_date:
            query["payment_date"] = {"$lte": end_date}
        
        payments = []
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        async for payment in cursor:
            payment["_id"] = str(payment["_id"])
            payments.append(payment)
        return payments

    async def get_total_count(self, sale_id: Optional[str] = None,
                             payment_method: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None):
        query = {}
        
        if sale_id:
            query["sale_id"] = sale_id
            
        if payment_method:
            query["payment_method"] = payment_method
            
        if start_date and end_date:
            query["payment_date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["payment_date"] = {"$gte": start_date}
        elif end_date:
            query["payment_date"] = {"$lte": end_date}
            
        return await self.collection.count_documents(query)
    
    async def get_by_id(self, payment_id: str):
        try:
            payment = await self.collection.find_one({"_id": ObjectId(payment_id)})
            if payment:
                payment["_id"] = str(payment["_id"])
            return payment
        except Exception:
            return None

    async def get_by_sale_id(self, sale_id: str):
        """Lấy tất cả payments của một sale"""
        payments = []
        async for payment in self.collection.find({"sale_id": sale_id}).sort("created_at", -1):
            payment["_id"] = str(payment["_id"])
            payments.append(payment)
        return payments
        
    async def create(self, payment_data: PaymentCreate, created_by: str):
        payment_dict = payment_data.model_dump()
        payment_dict["created_by"] = created_by
        payment_dict["payment_date"] = datetime.utcnow()
        payment_dict["created_at"] = datetime.utcnow()

        result = await self.collection.insert_one(payment_dict)
        payment_dict["_id"] = str(result.inserted_id)
        
        # Cập nhật payment status của sale
        await self._update_sale_payment_status(payment_data.sale_id)
        
        return payment_dict
    
    async def delete(self, payment_id: str):
        try:
            payment = await self.get_by_id(payment_id)
            if not payment:
                return False
                
            result = await self.collection.delete_one({"_id": ObjectId(payment_id)})
            
            if result.deleted_count > 0:
                # Cập nhật lại payment status của sale
                await self._update_sale_payment_status(payment["sale_id"])
                return True
            return False
        except Exception: 
            return False

    async def _update_sale_payment_status(self, sale_id: str):
        """Cập nhật trạng thái thanh toán của sale"""
        try:
            # Lấy thông tin sale
            sale = await self.db.sales.find_one({"_id": ObjectId(sale_id)})
            if not sale:
                return
            
            # Tính tổng đã thanh toán
            total_paid = 0
            async for payment in self.collection.find({"sale_id": sale_id}):
                total_paid += payment["amount"]
            
            # Xác định trạng thái thanh toán
            sale_amount = sale["total_amount"]
            if total_paid <= 0:
                payment_status = "pending"
            elif total_paid >= sale_amount:
                payment_status = "paid"
            else:
                payment_status = "partial"
            
            # Cập nhật sale
            await self.db.sales.update_one(
                {"_id": ObjectId(sale_id)},
                {"$set": {"payment_status": payment_status, "updated_at": datetime.utcnow()}}
            )
        except Exception:
            pass