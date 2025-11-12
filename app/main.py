from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database.db import engine, Base
from app.database import models
from app.routes import auth, products, customers, suppliers, sales, inventory, payments, promotions, reports
from app.middleware.response_middleware import ResponseWrapperMiddleware
import os

# Tạo thư mục uploads nếu chưa có
os.makedirs("uploads/products", exist_ok=True)

# Tạo tất cả bảng
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Furniture Management API",
    description="API cho ứng dụng quản lý nội thất",
    version="1.0.0"
)

# Mount static files để serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Response Wrapper Middleware (phải đặt trước CORS)
app.add_middleware(ResponseWrapperMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(suppliers.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(payments.router)
app.include_router(promotions.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"message": "Furniture Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)