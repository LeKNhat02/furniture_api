from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database.db import connect_to_mongo, close_mongo_connection, get_database
from app.routes import auth, products, customers, sales, suppliers, promotions, payments, reports, inventory
from app.services.user_service import UserService
from app.services.demo_data_service import DemoDataService

# Load environment variables
load_dotenv("db.env")

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

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")
app.include_router(promotions.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Furniture Management API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)