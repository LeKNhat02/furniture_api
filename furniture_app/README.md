# furniture_app

Ứng dụng quản lý cửa hàng đồ nội thất (Flutter)

Tổng quan
- Ứng dụng Flutter để quản lý sản phẩm, tồn kho, khách hàng, nhà cung cấp, chương trình khuyến mãi, bán hàng, thanh toán và báo cáo.
- Sử dụng Provider cho state management và có lớp service để gọi API (ApiService, AuthService, ...).

Chức năng chính
- Xác thực: màn hình đăng nhập (lib/screens/auth/login_screen.dart) qua AuthProvider/AuthService.
- Quản lý sản phẩm: danh sách, chi tiết, thêm, sửa (lib/screens/product/, ProductProvider, ProductService).
- Tồn kho: xem giao dịch, thêm giao dịch tồn kho (inventory_provider, InventoryService).
- Bán hàng: tạo hóa đơn bán hàng, danh sách, chi tiết (SaleProvider, SaleService).
- Khách hàng & Nhà cung cấp: CRUD (customer_provider, supplier_provider và màn hình tương ứng).
- Khuyến mãi: tạo, sửa, danh sách (PromotionProvider, PromotionService).
- Thanh toán: thêm, danh sách, chi tiết thanh toán (PaymentProvider, PaymentService).
- Dashboard & Báo cáo: biểu đồ và tổng hợp (lib/screens/home/dashboard_screen.dart; widgets/charts).

Cấu trúc mã nguồn (tóm tắt)
- lib/main.dart — entry point, cấu hình Provider và routes.
- lib/providers/ — ChangeNotifier providers quản lý state.
- lib/core/services/ — lớp gọi API và logic nghiệp vụ.
- lib/core/models/ — các model dữ liệu (User, Product, Sale, Inventory, Customer, Supplier, Promotion, Payment).
- lib/screens/ — các màn hình theo chức năng.
- lib/widgets/ — các widget dùng chung (cards, forms, dialogs, charts).
- lib/core/config/ — hằng số và cấu hình môi trường.

Cài đặt & chạy
1. Cài đặt Flutter (stable) và công cụ platform.
2. Từ thư mục project: 
   - flutter pub get
   - flutter run -d <device>
3. Android: mở project bằng Android Studio hoặc chạy ./gradlew assembleDebug.
4. iOS: mở workspace trên Xcode để cấu hình signing.

Cấu hình môi trường
- Kiểm tra lib/core/config/constants.dart và lib/core/config/app_config.dart để cập nhật base URL API, key hoặc flag môi trường.
- Token và header xác thực được xử lý trong AuthService/ApiService — đảm bảo backend tương thích.

Hướng dẫn phát triển ngắn
1. Thêm model mới: lib/core/models/.
2. Thêm service: lib/core/services/<feature>_service.dart để gọi endpoint mới.
3. Thêm provider: lib/providers/ để quản lý state và expose method async.
4. Tạo màn hình: lib/screens/<feature>/, dùng lại widget trong lib/widgets/.
5. Đăng ký provider trong main.dart và thêm route nếu cần.

Gợi ý sửa lỗi phổ biến
- Lỗi null-safety: kiểm tra parsing từ API và thêm xử lý null cho các trường có thể thiếu.
- Lỗi API: kiểm tra base URL và header (AuthService).
- Form/validation: sử dụng formKey và validate trước khi gửi.
- State không cập nhật UI: gọi notifyListeners() sau khi thay đổi dữ liệu trong provider.
- Chạy flutter analyze để tìm vấn đề tĩnh.

Kiểm thử
- Hiện chưa có test mẫu. Nên thêm test đơn vị và widget trong thư mục test/.

Muốn tôi làm gì tiếp theo?
- Tạo file README.md hoàn chỉnh (đã xong).
- Viết hướng dẫn khởi tạo chi tiết hơn hoặc script cài đặt.
- Kiểm tra và sửa lỗi cụ thể (gửi log lỗi hoặc miêu tả vấn đề mà bạn gặp phải).
