from datetime import datetime

class ReportService:
    def __init__(self, db):
        self.db = db

    async def get_dashboard_stats(self):
        """Lấy thống kê tổng quan cho dashboard"""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Doanh thu hôm nay
        today_revenue = await self._get_revenue(today_start, now)
        
        # Doanh thu tháng này
        month_revenue = await self._get_revenue(month_start, now)
        
        # Số đơn hàng hôm nay
        today_orders = await self.db.sales.count_documents({
            "sale_date": {"$gte": today_start, "$lte": now}
        })
        
        # Số đơn hàng tháng này
        month_orders = await self.db.sales.count_documents({
            "sale_date": {"$gte": month_start, "$lte": now}
        })
        
        # Tổng khách hàng
        total_customers = await self.db.customers.count_documents({})
        
        # Tổng sản phẩm
        total_products = await self.db.products.count_documents({})
        
        # Sản phẩm sắp hết hàng
        low_stock_products = await self.db.products.count_documents({
            "$expr": {"$lte": ["$quantity", "$quantity_min"]}
        })
        
        return {
            "today_revenue": today_revenue,
            "month_revenue": month_revenue,
            "today_orders": today_orders,
            "month_orders": month_orders,
            "total_customers": total_customers,
            "total_products": total_products,
            "low_stock_products": low_stock_products
        }

    async def get_revenue_report(self, start_date: datetime, end_date: datetime, 
                                group_by: str = "day"):
        """Báo cáo doanh thu theo thời gian"""
        if group_by == "day":
            date_format = "%Y-%m-%d"
        elif group_by == "month":
            date_format = "%Y-%m"
        else:
            date_format = "%Y"
            
        pipeline = [
            {
                "$match": {
                    "sale_date": {"$gte": start_date, "$lte": end_date},
                    "payment_status": {"$in": ["paid", "partial"]}
                }
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": date_format, "date": "$sale_date"}},
                    "revenue": {"$sum": "$total_amount"},
                    "orders": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        result = []
        async for doc in self.db.sales.aggregate(pipeline):
            result.append({
                "date": doc["_id"],
                "revenue": doc["revenue"],
                "orders": doc["orders"]
            })
        
        return result

    async def get_top_products(self, start_date: datetime, end_date: datetime, 
                              limit: int = 10):
        """Top sản phẩm bán chạy"""
        pipeline = [
            {
                "$match": {
                    "sale_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.product_id",
                    "product_name": {"$first": "$items.product_name"},
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": "$items.total_price"}
                }
            },
            {"$sort": {"total_quantity": -1}},
            {"$limit": limit}
        ]
        
        result = []
        async for doc in self.db.sales.aggregate(pipeline):
            result.append({
                "product_id": doc["_id"],
                "product_name": doc["product_name"],
                "total_quantity": doc["total_quantity"],
                "total_revenue": doc["total_revenue"]
            })
        
        return result

    async def get_customer_report(self, start_date: datetime, end_date: datetime):
        """Báo cáo khách hàng"""
        pipeline = [
            {
                "$match": {
                    "sale_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$customer_id",
                    "customer_name": {"$first": "$customer_name"},
                    "total_orders": {"$sum": 1},
                    "total_spent": {"$sum": "$total_amount"}
                }
            },
            {"$sort": {"total_spent": -1}}
        ]
        
        result = []
        async for doc in self.db.sales.aggregate(pipeline):
            if doc["_id"]:  # Chỉ lấy khách hàng có ID
                result.append({
                    "customer_id": doc["_id"],
                    "customer_name": doc["customer_name"],
                    "total_orders": doc["total_orders"],
                    "total_spent": doc["total_spent"]
                })
        
        return result

    async def get_inventory_report(self):
        """Báo cáo tồn kho"""
        pipeline = [
            {
                "$project": {
                    "name": 1,
                    "category": 1,
                    "quantity": 1,
                    "quantity_min": 1,
                    "cost": 1,
                    "price": 1,
                    "inventory_value": {"$multiply": ["$quantity", "$cost"]},
                    "status": {
                        "$cond": {
                            "if": {"$lte": ["$quantity", "$quantity_min"]},
                            "then": "low_stock",
                            "else": "normal"
                        }
                    }
                }
            },
            {"$sort": {"quantity": 1}}
        ]
        
        result = []
        async for doc in self.db.products.aggregate(pipeline):
            doc["_id"] = str(doc["_id"])
            result.append(doc)
        
        return result

    async def _get_revenue(self, start_date: datetime, end_date: datetime):
        """Tính doanh thu trong khoảng thời gian"""
        pipeline = [
            {
                "$match": {
                    "sale_date": {"$gte": start_date, "$lte": end_date},
                    "payment_status": {"$in": ["paid", "partial"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$total_amount"}
                }
            }
        ]
        
        result = await self.db.sales.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0