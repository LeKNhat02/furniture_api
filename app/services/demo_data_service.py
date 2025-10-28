from app.services.product_service import ProductService
from app.schemas.product import ProductCreate
from datetime import datetime

class DemoDataService:
    def __init__(self, db):
        self.db = db
        self.product_service = ProductService(db)

    async def create_demo_products(self):
        """Tạo dữ liệu demo cho sản phẩm"""
        
        # Kiểm tra xem đã có sản phẩm demo chưa
        existing = await self.db.products.find_one({"sku": "DEMO-001"})
        if existing:
            return
        
        demo_products = [
            {
                "name": "Bàn ăn gỗ tự nhiên",
                "category": "Bàn ăn",
                "price": 15000000,
                "cost": 10000000,
                "quantity": 25,
                "quantity_min": 5,
                "description": "Bàn ăn 6 ghế bằng gỗ tự nhiên cao cấp",
                "sku": "DEMO-001"
            },
            {
                "name": "Ghế sofa da thật",
                "category": "Ghế sofa",
                "price": 25000000,
                "cost": 18000000,
                "quantity": 10,
                "quantity_min": 3,
                "description": "Ghế sofa 3 chỗ ngồi bọc da thật nhập khẩu",
                "sku": "DEMO-002"
            },
            {
                "name": "Tủ quần áo 4 cánh",
                "category": "Tủ",
                "price": 12000000,
                "cost": 8000000,
                "quantity": 15,
                "quantity_min": 4,
                "description": "Tủ quần áo 4 cánh có gương, ngăn kéo",
                "sku": "DEMO-003"
            },
            {
                "name": "Giường ngủ 1m8",
                "category": "Giường",
                "price": 8000000,
                "cost": 5500000,
                "quantity": 20,
                "quantity_min": 5,
                "description": "Giường ngủ 1m8 có hộc tủ tiện lợi",
                "sku": "DEMO-004"
            },
            {
                "name": "Bàn làm việc hiện đại",
                "category": "Bàn làm việc",
                "price": 4500000,
                "cost": 3000000,
                "quantity": 12,
                "quantity_min": 3,
                "description": "Bàn làm việc có ngăn kéo, thiết kế hiện đại",
                "sku": "DEMO-005"
            },
            {
                "name": "Kệ tivi gỗ",
                "category": "Kệ",
                "price": 6000000,
                "cost": 4000000,
                "quantity": 8,
                "quantity_min": 2,
                "description": "Kệ tivi 3 tầng bằng gỗ MDF cao cấp",
                "sku": "DEMO-006"
            },
            {
                "name": "Ghế xoay văn phòng",
                "category": "Ghế văn phòng",
                "price": 2500000,
                "cost": 1800000,
                "quantity": 30,
                "quantity_min": 8,
                "description": "Ghế xoay có tựa lưng cao, êm ái",
                "sku": "DEMO-007"
            },
            {
                "name": "Tủ bếp tủ chén",
                "category": "Tủ bếp",
                "price": 18000000,
                "cost": 13000000,
                "quantity": 6,
                "quantity_min": 2,
                "description": "Tủ bếp gỗ công nghiệp chống ẩm",
                "sku": "DEMO-008"
            }
        ]

        for product_data in demo_products:
            product = ProductCreate(**product_data)
            await self.product_service.create(product)
        
        print("Demo products created successfully!")

    async def create_demo_customers(self):
        """Tạo dữ liệu demo cho khách hàng"""
        from app.services.customer_service import CustomerService
        from app.schemas.customer import CustomerCreate
        
        customer_service = CustomerService(self.db)
        
        # Kiểm tra xem đã có khách hàng demo chưa
        existing = await self.db.customers.find_one({"phone": "0123456789"})
        if existing:
            return
            
        demo_customers = [
            {
                "name": "Nguyễn Văn An",
                "phone": "0123456789",
                "email": "nguyenvanan@email.com",
                "address": "123 Đường Nguyễn Trãi, Quận 1, TP.HCM",
                "customer_type": "vip"
            },
            {
                "name": "Trần Thị Bình",
                "phone": "0987654321",
                "email": "tranthibinh@email.com", 
                "address": "456 Đường Lê Lợi, Quận 3, TP.HCM",
                "customer_type": "regular"
            },
            {
                "name": "Lê Văn Cường",
                "phone": "0369852147",
                "email": "levancuong@email.com",
                "address": "789 Đường Võ Văn Tần, Quận 10, TP.HCM", 
                "customer_type": "regular"
            }
        ]

        for customer_data in demo_customers:
            customer = CustomerCreate(**customer_data)
            await customer_service.create(customer)
            
        print("Demo customers created successfully!")

    async def create_demo_suppliers(self):
        """Tạo dữ liệu demo cho nhà cung cấp"""
        from app.services.supplier_service import SupplierService
        from app.schemas.supplier import SupplierCreate
        
        supplier_service = SupplierService(self.db)
        
        # Kiểm tra xem đã có supplier demo chưa
        existing = await self.db.suppliers.find_one({"phone": "0281234567"})
        if existing:
            return
            
        demo_suppliers = [
            {
                "name": "Công ty TNHH Nội thất Hoàng Gia",
                "contact_person": "Nguyễn Văn Hoàng",
                "phone": "0281234567",
                "email": "contact@hoanggia.com",
                "address": "100 Đường Tô Hiến Thành, Quận 10, TP.HCM",
                "tax_code": "0123456789"
            },
            {
                "name": "Nhà máy gỗ Minh Phát",
                "contact_person": "Trần Văn Minh", 
                "phone": "0271234567",
                "email": "info@minhphat.com",
                "address": "200 Đường Quang Trung, Gò Vấp, TP.HCM",
                "tax_code": "0987654321"
            }
        ]

        for supplier_data in demo_suppliers:
            supplier = SupplierCreate(**supplier_data)
            await supplier_service.create(supplier)
            
        print("Demo suppliers created successfully!")