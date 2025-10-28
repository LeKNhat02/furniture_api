from fastapi import APIRouter, Query
from app.database.db import get_database
from app.services.product_service import ProductService
from typing import Optional

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/low-stock", response_model=list)
async def get_low_stock_products():
    """Lấy danh sách sản phẩm sắp hết hàng"""
    db = get_database()
    service = ProductService(db)
    
    # Query sản phẩm có quantity <= quantity_min
    pipeline = [
        {
            "$match": {
                "$expr": {"$lte": ["$quantity", "$quantity_min"]},
                "is_active": True
            }
        },
        {
            "$project": {
                "name": 1,
                "category": 1,
                "quantity": 1,
                "quantity_min": 1,
                "sku": 1,
                "shortage": {"$subtract": ["$quantity_min", "$quantity"]}
            }
        },
        {"$sort": {"shortage": -1}}
    ]
    
    products = []
    async for product in db.products.aggregate(pipeline):
        product["_id"] = str(product["_id"])
        products.append(product)
    
    return products

@router.get("/movements", response_model=dict)
async def get_inventory_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    product_id: Optional[str] = Query(None),
    movement_type: Optional[str] = Query(None)
):
    """Lấy lịch sử xuất nhập kho"""
    db = get_database()
    
    query = {}
    if product_id:
        query["product_id"] = product_id
    if movement_type:
        query["movement_type"] = movement_type
    
    movements = []
    cursor = db.inventory_movements.find(query).sort("created_at", -1).skip(skip).limit(limit)
    async for movement in cursor:
        movement["_id"] = str(movement["_id"])
        movements.append(movement)
    
    total = await db.inventory_movements.count_documents(query)
    
    return {
        "movements": movements,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/adjust/{product_id}")
async def adjust_inventory(
    product_id: str,
    quantity: int = Query(...),
    reason: str = Query("adjustment"),
    notes: Optional[str] = Query(None)
):
    """Điều chỉnh tồn kho"""
    db = get_database()
    service = ProductService(db)
    
    # Kiểm tra sản phẩm tồn tại
    product = await service.get_by_id(product_id)
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Cập nhật số lượng
    try:
        from bson import ObjectId
        from datetime import datetime
        
        await db.products.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$inc": {"quantity": quantity},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Ghi lại movement
        movement = {
            "product_id": product_id,
            "movement_type": "import" if quantity > 0 else "export",
            "quantity": quantity,
            "reason": reason,
            "notes": notes,
            "created_by": "user_placeholder",  # TODO: Lấy từ auth
            "created_at": datetime.utcnow()
        }
        await db.inventory_movements.insert_one(movement)
        
        return {"message": "Inventory adjusted successfully"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))