from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem, Exercise


# ================= QUẢN LÝ SẢN PHẨM =================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Số dòng trống hiển thị sẵn để up ảnh phụ


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    search_fields = ('name',)
    inlines = [ProductImageInline]


# ================= QUẢN LÝ BÀI TẬP (PHẦN BỔ SUNG ĐỂ FIX LỖI) =================
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    # list_display giúp hiện tên bài tập ra danh sách để bạn có thể bấm vào sửa
    list_display = ('name', 'muscle_group', 'created_at')

    # Cho phép bấm vào tên bài tập để mở trang chỉnh sửa
    list_display_links = ('name',)

    # Bộ lọc nhanh theo nhóm cơ bên tay phải
    list_filter = ('muscle_group',)

    # Ô tìm kiếm theo tên bài tập
    search_fields = ('name', 'muscle_group')


# ================= QUẢN LÝ ĐƠN HÀNG =================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 1. Hiển thị thông tin cơ bản ngoài danh sách
    list_display = ('id', 'full_name', 'total_amount', 'status', 'created_at')

    # 2. Tối ưu cho MongoDB (Tắt các tính năng Join bảng phức tạp nếu cần)
    # inlines = [OrderItemInline] # Nếu mở dòng này mà lỗi thì cứ comment lại như cũ

    # 3. Dùng ID để chọn User thay vì Menu thả xuống (Tránh lag khi nhiều User)
    raw_id_fields = ('user',)

    # 4. Các trường cho phép sửa bên trong trang chi tiết
    fields = ('user', 'full_name', 'email', 'phone', 'address', 'total_amount', 'payment_method', 'status',
              'cancel_reason')