from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ================= SẢN PHẨM =================
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

    # 2 TRƯỜNG MỚI THÊM VÀO
    import_price = models.IntegerField(default=0, verbose_name="Giá nhập (VNĐ)")
    stock = models.IntegerField(default=0, verbose_name="Số lượng tồn kho")

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


# ================= GIỎ HÀNG =================
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


# ================= ĐƠN HÀNG =================
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
    is_paid = models.BooleanField(default=False, verbose_name="Đã thanh toán")
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


# ================= BÀI TẬP (PHẦN BỊ THIẾU) =================
class Exercise(models.Model):
    MUSCLE_CHOICES = [
        ('CHEST', 'NGỰC'),
        ('BACK', 'LƯNG / XÔ'),
        ('LEGS', 'CHÂN / MÔNG'),
        ('SHOULDERS', 'VAI'),
        ('BICEPS', 'TAY TRƯỚC'),
        ('TRICEPS', 'TAY SAU'),
        ('ABS', 'BỤNG'),
        ('CARDIO', 'TIM MẠCH'),
    ]

    name = models.CharField(max_length=200, verbose_name="Tên bài tập")
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_CHOICES, verbose_name="Nhóm cơ chính")
    description = models.TextField(verbose_name="Hướng dẫn chi tiết")

    # Ảnh minh họa
    image = models.FileField(upload_to='exercises/videos/', null=True, blank=True)

    # THAY ĐỔI TẠI ĐÂY: Dùng FileField thay vì URLField để nhận file .mp4
    video_file = models.FileField(
        upload_to='exercises/videos/',
        null=True,
        blank=True,
        verbose_name="Video bài tập (.mp4)"
    )

    # (Tùy chọn) Giữ lại cái này nếu bạn vẫn muốn dán link Youtube đôi khi
    video_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="Link Video (YouTube)")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_muscle_group_display()}"


class Coupon(models.Model):
    DISCOUNT_CHOICES = (
        ('PERCENTAGE', 'Giảm theo phần trăm (%)'),
        ('FIXED', 'Giảm theo số tiền cố định (VNĐ)'),
    )

    code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_CHOICES, default='FIXED',
                                     verbose_name="Loại giảm giá")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá trị giảm")

    # Các điều kiện
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Đơn hàng tối thiểu")
    valid_from = models.DateTimeField(verbose_name="Ngày bắt đầu")
    valid_to = models.DateTimeField(verbose_name="Ngày hết hạn")
    active = models.BooleanField(default=True, verbose_name="Đang kích hoạt")

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    # --- ĐÂY LÀ 2 BIẾN ẢO DÙNG ĐỂ HIỂN THỊ HTML (TRỊ BỆNH MONGODB) ---
    @property
    def val_display(self):
        # Dịch Decimal128 sang số Float thông thường
        return float(str(self.value)) if self.value else 0

    @property
    def min_display(self):
        return float(str(self.min_purchase)) if self.min_purchase else 0
    # ------------------------------------------------------------------

    class Meta:
        verbose_name = "Mã giảm giá"
        verbose_name_plural = "Quản lý Mã giảm giá"