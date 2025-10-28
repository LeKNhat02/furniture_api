# Furniture Management API

API quản lý bán hàng nội thất được xây dựng với FastAPI và MongoDB.

## 🚀 Tính năng

### 1. **Quản lý người dùng** (`/api/auth`)
- Đăng nhập với username/password
- Hệ thống phân quyền (admin/staff)
- Demo users:
  - Username: `admin`, Password: `password123` (Admin)
  - Username: `staff`, Password: `password123` (Staff)

### 2. **Quản lý sản phẩm** (`/api/products`)
- CRUD sản phẩm
- Tìm kiếm theo tên, mô tả, SKU
- Lọc theo danh mục
- Quản lý tồn kho (quantity, quantity_min)

### 3. **Quản lý khách hàng** (`/api/customers`)
- CRUD khách hàng
- Tìm kiếm theo tên, SĐT, email
- Theo dõi tổng chi tiêu và số đơn hàng

### 4. **Quản lý bán hàng** (`/api/sales`)
- Tạo đơn hàng với nhiều sản phẩm
- Tự động tạo mã đơn hàng
- Quản lý trạng thái thanh toán
- Tự động cập nhật tồn kho

### 5. **Quản lý nhà cung cấp** (`/api/suppliers`)
- CRUD nhà cung cấp
- Thông tin liên hệ, thông tin ngân hàng
- Điều kiện thanh toán

### 6. **Quản lý khuyến mãi** (`/api/promotions`)
- Tạo các loại khuyến mãi: giảm %, giảm số tiền cố định
- Áp dụng cho sản phẩm cụ thể
- Giới hạn thời gian và số lần sử dụng

### 7. **Quản lý thanh toán** (`/api/payments`)
- Ghi nhận thanh toán cho đơn hàng
- Hỗ trợ nhiều phương thức: tiền mặt, thẻ, chuyển khoản, trả góp
- Tự động cập nhật trạng thái thanh toán của đơn hàng

### 8. **Quản lý kho hàng** (`/api/inventory`)
- Theo dõi sản phẩm sắp hết hàng
- Lịch sử xuất nhập kho
- Điều chỉnh tồn kho

### 9. **Báo cáo** (`/api/reports`)
- Dashboard thống kê tổng quan
- Báo cáo doanh thu theo thời gian
- Top sản phẩm bán chạy
- Báo cáo khách hàng
- Báo cáo tồn kho

## 🛠️ Cài đặt

### Yêu cầu
- Python 3.8+
- MongoDB
- pip

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Cấu hình database
1. Khởi động MongoDB
2. Cập nhật file `db.env` nếu cần:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=furniture_db
```

### Chạy ứng dụng
```bash
python main.py
```

Hoặc với uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 API Documentation

Sau khi chạy server, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Demo Data

Khi khởi động lần đầu, hệ thống sẽ tự động tạo:
- **Demo users**: admin/staff
- **Demo products**: 8 sản phẩm nội thất
- **Demo customers**: 3 khách hàng
- **Demo suppliers**: 2 nhà cung cấp

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Đăng nhập

### Products
- `GET /api/products` - Danh sách sản phẩm (có search & filter)
- `GET /api/products/{id}` - Chi tiết sản phẩm
- `POST /api/products` - Tạo sản phẩm mới
- `PUT /api/products/{id}` - Cập nhật sản phẩm
- `DELETE /api/products/{id}` - Xóa sản phẩm

### Customers
- `GET /api/customers` - Danh sách khách hàng (có search)
- `GET /api/customers/{id}` - Chi tiết khách hàng
- `POST /api/customers` - Tạo khách hàng mới
- `PUT /api/customers/{id}` - Cập nhật khách hàng
- `DELETE /api/customers/{id}` - Xóa khách hàng

### Sales
- `GET /api/sales` - Danh sách đơn hàng (có filter)
- `GET /api/sales/{id}` - Chi tiết đơn hàng
- `POST /api/sales` - Tạo đơn hàng mới
- `PUT /api/sales/{id}` - Cập nhật đơn hàng
- `DELETE /api/sales/{id}` - Xóa đơn hàng

### Suppliers
- `GET /api/suppliers` - Danh sách nhà cung cấp
- `GET /api/suppliers/{id}` - Chi tiết nhà cung cấp
- `POST /api/suppliers` - Tạo nhà cung cấp mới
- `PUT /api/suppliers/{id}` - Cập nhật nhà cung cấp
- `DELETE /api/suppliers/{id}` - Xóa nhà cung cấp

### Promotions
- `GET /api/promotions` - Danh sách khuyến mãi
- `GET /api/promotions/applicable` - Khuyến mãi áp dụng được
- `GET /api/promotions/{id}` - Chi tiết khuyến mãi
- `POST /api/promotions` - Tạo khuyến mãi mới
- `PUT /api/promotions/{id}` - Cập nhật khuyến mãi
- `DELETE /api/promotions/{id}` - Xóa khuyến mãi

### Payments
- `GET /api/payments` - Danh sách thanh toán
- `GET /api/payments/by-sale/{sale_id}` - Thanh toán của đơn hàng
- `GET /api/payments/{id}` - Chi tiết thanh toán
- `POST /api/payments` - Ghi nhận thanh toán mới
- `DELETE /api/payments/{id}` - Xóa thanh toán

### Inventory
- `GET /api/inventory/low-stock` - Sản phẩm sắp hết hàng
- `GET /api/inventory/movements` - Lịch sử xuất nhập kho
- `POST /api/inventory/adjust/{product_id}` - Điều chỉnh tồn kho

### Reports
- `GET /api/reports/dashboard` - Thống kê dashboard
- `GET /api/reports/revenue` - Báo cáo doanh thu
- `GET /api/reports/top-products` - Top sản phẩm bán chạy
- `GET /api/reports/customers` - Báo cáo khách hàng
- `GET /api/reports/inventory` - Báo cáo tồn kho

## 💡 Ví dụ sử dụng

### Đăng nhập
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password123"}'
```

### Lấy danh sách sản phẩm
```bash
curl "http://localhost:8000/api/products?search=bàn&limit=10"
```

### Tạo đơn hàng mới
```bash
curl -X POST "http://localhost:8000/api/sales" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_id": "customer_id_here",
       "items": [
         {
           "product_id": "product_id_here",
           "product_name": "Bàn ăn gỗ",
           "quantity": 1,
           "unit_price": 15000000,
           "total_price": 15000000
         }
       ],
       "subtotal": 15000000,
       "total_amount": 15000000
     }'
```

## 🔧 Cấu trúc Project

```
furniture_api/
├── app/
│   ├── models/          # Data models
│   ├── schemas/         # Pydantic schemas
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   └── database/        # Database connection
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── db.env              # Environment variables
└── README.md           # Documentation
```

## 🎯 Tương thích với Flutter Frontend

Backend này được thiết kế để hoàn toàn tương thích với cấu trúc Flutter frontend đã cung cấp:

- ✅ **Authentication**: JWT tokens cho login/logout
- ✅ **Products**: CRUD với search/filter 
- ✅ **Customers**: Quản lý khách hàng
- ✅ **Sales**: Bán hàng với cart và checkout
- ✅ **Suppliers**: Quản lý nhà cung cấp
- ✅ **Promotions**: Hệ thống khuyến mãi
- ✅ **Payments**: Thanh toán đa phương thức
- ✅ **Inventory**: Quản lý kho hàng
- ✅ **Reports**: Dashboard và báo cáo chi tiết

## 🚀 Triển khai Production

### Cải thiện bảo mật
1. Thay đổi `JWT_SECRET_KEY` trong production
2. Sử dụng HTTPS
3. Cấu hình CORS origins cụ thể
4. Thêm rate limiting
5. Implement proper authentication middleware

### Database
1. Sử dụng MongoDB Atlas hoặc MongoDB cluster
2. Tạo indexes cho performance
3. Backup định kỳ

### Monitoring
1. Thêm logging
2. Health checks
3. Error tracking
4. Performance monitoring