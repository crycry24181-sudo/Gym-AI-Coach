from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('WHEY', 'Whey Protein'),
        ('CREATINE', 'Creatine'),
        ('EAA', 'EAA / BCAA'),
        ('HEALTH', 'Vitamin & Khoáng chất'),
        ('PRE', 'Pre-workout (Tăng sức mạnh)'),
        ('ACCESSORIES', 'Dụng cụ hỗ trợ tập luyện'),
    ]

    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Loại")
    price = models.IntegerField(verbose_name="Giá tiền (VNĐ)")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Ảnh sản phẩm")
    description = models.TextField(blank=True, verbose_name="Mô tả")

    def __str__(self):
        return self.name
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Ảnh phụ")

    def __str__(self):
        return f"Ảnh của {self.product.name}"


# --- GIỎ HÀNG (Tạm thời) ---
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Giỏ hàng của {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity


# --- ĐƠN HÀNG (Lưu trữ lịch sử mua) ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xác nhận'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('SHIPPING', 'Đang giao hàng'),
        ('COMPLETED', 'Hoàn thành'),
        ('CANCELLED', '⛔ Đã bị từ chối'),
    ]
    PAYMENT_METHODS = [
        ('COD', 'Thanh toán khi nhận hàng (COD)'),
        ('BANK', 'Chuyển khoản ngân hàng'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, verbose_name="Người nhận")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ nhận hàng")

    total_amount = models.IntegerField(verbose_name="Tổng tiền")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='COD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cancel_reason = models.TextField(blank=True, null=True, verbose_name="Lý do từ chối đơn (nếu có)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()  # Lưu giá tại thời điểm mua

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='product_gallery/')

    def __str__(self):
        return f"Ảnh của {self.product.name}"


# store/models.py

class Exercise(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên bài tập")

    # 👇 Dùng FileField để chấp nhận cả GIF và Video (MP4)
    video_file = models.FileField(
        upload_to='exercises/videos/',
        verbose_name="Video/GIF hướng dẫn",
        blank=True, null=True
    )

    # Mô tả cách tập
    description = models.TextField(blank=True, verbose_name="Hướng dẫn chi tiết")

    # Phân loại nhóm cơ
    MUSCLE_CHOICES = [
        ('CHEST', 'Ngực'),
        ('BACK', 'Lưng/Xô'),
        ('LEGS', 'Chân/Mông'),
        ('SHOULDERS', 'Vai'),
        ('BICEPS', 'Tay trước'),
        ('TRICEPS', 'Tay sau'),
        ('ABS', 'Bụng'),
        ('CARDIO', 'Tim mạch'),
    ]
    muscle_group = models.CharField(
        max_length=50,
        choices=MUSCLE_CHOICES,
        default='CHEST',
        verbose_name="Nhóm cơ"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models

# Create your models here.
