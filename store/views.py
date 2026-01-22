import threading  # Dùng để gửi mail chạy ngầm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings

# Import Models và Forms
from .models import Product, ProductImage, Cart, CartItem, Order, OrderItem, Exercise
from users.models import Profile
from .forms import ProductForm, ExerciseForm


# ================= CẤU HÌNH GỬI MAIL CHẠY NGẦM =================
class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            self.message,
            settings.EMAIL_HOST_USER,
            self.recipient_list,
            fail_silently=False,
        )


# ================= TRANG CỬA HÀNG (USER) =================

def store_view(request):
    """Hiển thị danh sách sản phẩm chia theo danh mục"""
    all_products = list(Product.objects.all())
    products_by_category = []

    for cat_code, cat_name in Product.CATEGORY_CHOICES:
        products_in_group = [p for p in all_products if p.category == cat_code]
        if products_in_group:
            products_by_category.append({
                'category_name': cat_name,
                'products': products_in_group
            })

    return render(request, 'store/product_list.html', {'products_by_category': products_by_category})


def product_detail(request, pk):
    """Xem chi tiết 1 sản phẩm"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


# ================= TRANG BÀI TẬP (USER - PUBLIC) =================

def exercise_list(request, muscle_group=None):
    """Hiển thị danh sách bài tập (có lọc theo nhóm cơ)"""
    if muscle_group:
        exercises = Exercise.objects.filter(muscle_group=muscle_group).order_by('-created_at')
        muscle_names = {
            'CHEST': 'NGỰC',
            'BACK': 'LƯNG / XÔ',
            'LEGS': 'CHÂN / MÔNG',
            'SHOULDERS': 'VAI',
            'BICEPS': 'TAY TRƯỚC',
            'TRICEPS': 'TAY SAU',
            'ABS': 'BỤNG',
            'CARDIO': 'TIM MẠCH'
        }
        current_name = muscle_names.get(muscle_group, muscle_group)
    else:
        exercises = Exercise.objects.all().order_by('-created_at')
        current_name = "Tất cả bài tập"

    return render(request, 'exercises/exercise_list.html', {
        'exercises': exercises,
        'current_name': current_name
    })


def exercise_detail(request, pk):
    """Xem chi tiết 1 bài tập"""
    exercise = get_object_or_404(Exercise, pk=pk)
    return render(request, 'exercises/exercise_detail.html', {'exercise': exercise})


# ================= GIỎ HÀNG & THANH TOÁN =================

@login_required(login_url='login')
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"Đã thêm {product.name} vào giỏ!")

    if request.GET.get('buy_now'):
        return redirect('checkout')
    return redirect('cart')


@login_required(login_url='login')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required(login_url='login')
def update_cart_item(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id)
    if item.cart.user != request.user:
        return redirect('cart')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
    elif action == 'delete':
        item.delete()

    next_page = request.GET.get('next')
    if next_page == 'checkout':
        return redirect('checkout')
    return redirect('cart')


@login_required(login_url='login')
def checkout_view(request):
    """Trang thanh toán"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    if cart.items.count() == 0:
        messages.warning(request, "Giỏ hàng đang trống!")
        return redirect('store')

    user_profile = getattr(request.user, 'profile', None)
    initial_data = {
        'full_name': request.user.first_name,
        'email': request.user.email,
        'phone': user_profile.phone if user_profile else '',
        'address': ''
    }

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            email=request.POST.get('email'),
            payment_method=request.POST.get('payment_method'),
            total_amount=cart.total_price
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, product=item.product,
                quantity=item.quantity, price=item.product.price
            )

        cart.items.all().delete()
        return render(request, 'store/order_success.html', {'order': order})

    return render(request, 'store/checkout.html', {'cart': cart, 'user_info': initial_data})


@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})


# ================= QUẢN TRỊ (ADMIN / STAFF) =================

@staff_member_required(login_url='login')
def manage_orders(request):
    """Quản lý đơn hàng + GỬI EMAIL CHO MỌI TRẠNG THÁI"""
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')  # HTML gửi lên: CONFIRMED, SHIPPING...
            cancel_reason = request.POST.get('cancel_reason')

            order = Order.objects.get(id=order_id)

            # Lưu lại trạng thái cũ để kiểm tra (tùy chọn, để tránh spam nếu admin bấm lưu 2 lần)
            old_status = order.status

            # Cập nhật thông tin
            order.status = new_status
            if cancel_reason:
                order.cancel_reason = cancel_reason

            # Nếu Hoàn thành -> Đánh dấu đã trả tiền
            if new_status == 'COMPLETED':
                order.is_paid = True

            order.save()

            # === LOGIC GỬI EMAIL THEO TỪNG TRẠNG THÁI ===
            # Chỉ gửi nếu trạng thái thực sự thay đổi (tránh spam)
            if old_status != new_status:
                subject = ""
                message = ""

                # 1. ĐÃ XÁC NHẬN (CONFIRMED)
                if new_status == 'CONFIRMED':
                    subject = f"✅ Đơn hàng #{order.id} đã được xác nhận!"
                    message = f"""Xin chào {order.full_name},

Shop đã nhận được đơn hàng #{order.id} của bạn và đang tiến hành đóng gói.
Chúng tôi sẽ bàn giao cho đơn vị vận chuyển sớm nhất.

Cảm ơn bạn đã chờ đợi!"""

                # 2. ĐANG GIAO HÀNG (SHIPPING)
                elif new_status == 'SHIPPING':
                    subject = f"🚚 Đơn hàng #{order.id} đang trên đường giao đến bạn"
                    message = f"""Xin chào {order.full_name},

Shipper đã lấy hàng đi giao rồi nhé!
Bạn vui lòng để ý điện thoại để nhận hàng.

Chúc bạn một ngày tốt lành!"""

                # 3. HOÀN THÀNH (COMPLETED)
                elif new_status == 'COMPLETED':
                    subject = f"🎉 Giao thành công! Cảm ơn bạn đã mua hàng #{order.id}"
                    message = f"""Xin chào {order.full_name},

Hệ thống ghi nhận đơn hàng #{order.id} đã được giao thành công.
Hy vọng bạn hài lòng với sản phẩm. Hẹn gặp lại bạn lần sau nhé!"""

                # 4. ĐÃ HỦY (CANCELLED)
                elif new_status == 'CANCELLED':
                    subject = f"❌ Thông báo hủy đơn hàng #{order.id}"
                    message = f"""Xin chào {order.full_name},

Rất tiếc, đơn hàng #{order.id} của bạn đã bị hủy.
Lý do hủy: {order.cancel_reason if order.cancel_reason else 'Không có lý do cụ thể'}

Vui lòng liên hệ lại với Shop nếu cần hỗ trợ thêm nhé."""

                # --- TIẾN HÀNH GỬI MAIL ---
                if subject and order.email:
                    try:
                        EmailThread(subject, message, [order.email]).start()
                        messages.success(request, f"Đã cập nhật trạng thái '{new_status}' và gửi mail thành công!")
                    except Exception as e:
                        messages.warning(request, f"Đã cập nhật nhưng lỗi gửi mail: {e}")
                else:
                    messages.success(request,
                                     f"Đã cập nhật trạng thái (Không gửi mail do thiếu nội dung hoặc email khách).")
            else:
                messages.info(request, "Trạng thái không thay đổi, không gửi mail.")

        except Order.DoesNotExist:
            messages.error(request, "Không tìm thấy đơn hàng!")

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/manage_orders.html', {'orders': orders})


@staff_member_required(login_url='login')
def manage_products(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'store/manage_products.html', {'products': products})


@staff_member_required(login_url='login')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            if 'detail_images' in request.FILES:
                images = request.FILES.getlist('detail_images')
                for img in images:
                    ProductImage.objects.create(product=product, image=img)
            messages.success(request, f"Đã cập nhật '{product.name}' thành công!")
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form, 'product': product})


@staff_member_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            if 'detail_images' in request.FILES:
                images = request.FILES.getlist('detail_images')
                for img in images:
                    ProductImage.objects.create(product=product, image=img)
            messages.success(request, "Thêm sản phẩm thành công!")
            return redirect('manage_products')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


@staff_member_required(login_url='login')
def delete_product(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, "Đã xóa sản phẩm!")
    return redirect('manage_products')


@staff_member_required(login_url='login')
def delete_image(request, img_id):
    img = get_object_or_404(ProductImage, id=img_id)
    p_id = img.product.id
    img.delete()
    messages.success(request, "Đã xóa ảnh phụ!")
    return redirect('edit_product', pk=p_id)


# ================= QUẢN LÝ BÀI TẬP (ADMIN) =================

@staff_member_required(login_url='login')
def manage_exercises(request):
    exercises = Exercise.objects.all().order_by('-created_at')
    return render(request, 'exercises/manage_exercises.html', {'exercises': exercises})


@staff_member_required(login_url='login')
def add_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm bài tập thành công!')
            return redirect('manage_exercises')
    else:
        form = ExerciseForm()
    return render(request, 'exercises/add_exercise.html', {'form': form})


@staff_member_required(login_url='login')
def delete_exercise(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.delete()
    messages.success(request, 'Đã xóa bài tập!')
    return redirect('manage_exercises')