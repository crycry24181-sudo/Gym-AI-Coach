from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

# Gom các model vào 1 dòng cho gọn
from .models import Product, ProductImage, Cart, CartItem, Order, OrderItem
from users.models import Profile
from .forms import ProductForm


# ================= TRANG CỬA HÀNG (USER) =================

def store_view(request):
    """Hiển thị danh sách sản phẩm chia theo danh mục (Tránh lỗi Djongo)"""
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


# ================= GIỎ HÀNG & THANH TOÁN =================

@login_required(login_url='login')
def add_to_cart(request, pk):
    """Thêm sản phẩm vào giỏ"""
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
    """Cập nhật số lượng trong giỏ (từ trang Cart hoặc Checkout)"""
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
    """Trang thanh toán đơn hàng"""
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
    """Quản lý danh sách đơn hàng toàn hệ thống"""
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=request.POST.get('order_id'))
            order.status = request.POST.get('status')
            order.cancel_reason = request.POST.get('cancel_reason')
            order.save()
            messages.success(request, f"Đã cập nhật đơn hàng #{order.id}!")
        except Order.DoesNotExist:
            messages.error(request, "Không tìm thấy đơn hàng!")

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/manage_orders.html', {'orders': orders})


@staff_member_required(login_url='login')
def manage_products(request):
    """Danh sách sản phẩm để sửa/xóa"""
    products = Product.objects.all().order_by('-id')
    return render(request, 'store/manage_products.html', {'products': products})


@staff_member_required(login_url='login')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        # Form chỉ xử lý các trường chữ và ảnh đại diện chính
        form = ProductForm(request.POST, request.FILES, instance=product)

        # In ra Terminal để bạn theo dõi (Có thể xóa sau)
        print("FILES nhận được:", request.FILES)

        if form.is_valid():
            product = form.save()

            # TỰ TAY xử lý Album ảnh phụ (Không qua form.is_valid nữa)
            if 'detail_images' in request.FILES:
                images = request.FILES.getlist('detail_images')
                for img in images:
                    ProductImage.objects.create(product=product, image=img)
                print(f"Đã lưu thêm {len(images)} ảnh vào album.")

            messages.success(request, f"Đã cập nhật '{product.name}' thành công!")
            return redirect('manage_products')
        else:
            print("Lỗi Form:", form.errors)
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/edit_product.html', {'form': form, 'product': product})


# Hàm add_product cũng sửa tương tự:
@staff_member_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Xử lý album ảnh phụ
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