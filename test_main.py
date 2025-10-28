from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv("test.env")

# Test mode - simple server without MongoDB
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"

if TEST_MODE:
    print("🧪 Running in TEST MODE - MongoDB not required")
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("✅ Test server starting...")
        yield
        print("🛑 Test server shutting down...")
else:
    from app.database.db import connect_to_mongo, close_mongo_connection, get_database
    from app.services.user_service import UserService
    from app.services.demo_data_service import DemoDataService

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        await connect_to_mongo()
        db = get_database()
        
        # Tạo demo users
        user_service = UserService(db)
        await user_service.create_demo_users()
        
        # Tạo demo data
        demo_service = DemoDataService(db)
        await demo_service.create_demo_products()
        await demo_service.create_demo_customers()
        await demo_service.create_demo_suppliers()
        
        yield
        # Shutdown
        await close_mongo_connection()

# Initialize app
app = FastAPI(
    title="Furniture Management API",
    description="API quản lý bán hàng nội thất",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "mode": "test" if TEST_MODE else "production",
        "message": "Furniture Management API is running"
    }

@app.get("/")
async def root():
    return {
        "message": "Furniture Management API is running",
        "mode": "test" if TEST_MODE else "production",
        "docs": "http://localhost:8000/docs"
    }

# Include routers only in production mode
if not TEST_MODE:
    from app.routes import auth, products, customers, sales, suppliers, promotions, payments, reports, inventory
    
    app.include_router(auth.router, prefix="/api")
    app.include_router(products.router, prefix="/api")
    app.include_router(customers.router, prefix="/api")
    app.include_router(sales.router, prefix="/api")
    app.include_router(suppliers.router, prefix="/api")
    app.include_router(promotions.router, prefix="/api")
    app.include_router(payments.router, prefix="/api")
    app.include_router(reports.router, prefix="/api")
    app.include_router(inventory.router, prefix="/api")
else:
    # Test routes
    @app.get("/api/test")
    async def test_endpoint():
        return {
            "message": "Test endpoint working!",
            "features": [
                "Authentication & Users",
                "Products Management", 
                "Customer Management",
                "Sales Management",
                "Supplier Management", 
                "Promotions",
                "Payments",
                "Inventory Management",
                "Reports & Analytics"
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_main:app", host="0.0.0.0", port=8000, reload=True)