from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem

# Tạo form nhập ảnh phụ nằm gọn trong trang sản phẩm chính
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Số dòng trống hiển thị sẵn để up ảnh

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    search_fields = ('name',)
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 1. Chỉ hiển thị thông tin cơ bản
    list_display = ('id', 'full_name', 'total_amount', 'status', 'created_at')

    # 2. ❌ TẮT HẾT các tính năng gây lỗi cho MongoDB (Bộ lọc, Inlines)
    # list_filter = ('status', 'created_at')  <-- Nguyên nhân gây lỗi
    # inlines = [OrderItemInline]             <-- Nguyên nhân gây lỗi

    # 3. ✅ Dùng ID để chọn User thay vì Menu thả xuống (Giúp tránh lỗi Join bảng)
    raw_id_fields = ('user',)

    # 4. Các trường cho phép sửa
    fields = ('user', 'full_name', 'email', 'phone', 'address', 'total_amount', 'payment_method', 'status',
              'cancel_reason')