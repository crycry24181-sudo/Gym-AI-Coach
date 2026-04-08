import threading  # Dùng để gửi mail chạy ngầm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from collections import defaultdict
import json
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.http import JsonResponse

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
    # 1. Định nghĩa nội dung lợi ích cho từng nhóm cơ
    benefits_data = {
        'CHEST': 'Tập ngực giúp cơ thể phát triển cân đối và mạnh mẽ hơn, đặc biệt làm cho phần thân trên trở nên đầy đặn, rõ nét và nam tính hơn. Khi tập ngực, bạn không chỉ tăng kích thước cơ ngực mà còn cải thiện sức mạnh tổng thể, hỗ trợ tốt cho vai và tay sau trong các hoạt động hằng ngày như đẩy hoặc nâng vật nặng. Ngoài ra, cơ ngực khỏe còn góp phần cải thiện tư thế, giúp giữ vai ổn định hơn và hạn chế tình trạng gù lưng nếu kết hợp tập luyện hợp lý với lưng. Việc tăng khối lượng cơ cũng giúp cơ thể đốt nhiều calo hơn, hỗ trợ duy trì vóc dáng.',
        'BACK': 'Tập lưng xô giúp mở rộng phần thân trên, tạo dáng chữ V rõ ràng (vai rộng – eo nhỏ), từ đó làm tổng thể cơ thể nhìn cân đối và mạnh mẽ hơn. Ngoài yếu tố thẩm mỹ, lưng xô còn đóng vai trò quan trọng trong các động tác kéo và giữ ổn định cột sống, giúp giảm nguy cơ gù lưng nếu tập đúng cách..',
        'LEGS': 'Đây là nhóm cơ quan trọng nhất nhưng nhiều người lại hay bỏ qua. Chân và mông giúp bạn di chuyển, giữ thăng bằng, tăng sức mạnh toàn thân và còn kích thích cơ thể phát triển tốt hơn (do liên quan đến hormone). Nếu chân yếu thì gần như toàn bộ sức mạnh cơ thể cũng bị hạn chế.',
        'SHOULDERS': 'Cơ vai giúp thân trên trông rộng hơn, đặc biệt là phần vai ngang (vai giữa) tạo cảm giác “to khung người”. Vai khỏe cũng giúp bạn thực hiện tốt các động tác nâng, đẩy và hỗ trợ cho ngực, lưng trong nhiều bài tập khác. Ngoài ra, vai còn giúp ổn định khớp vai, giảm chấn thương nếu tập đúng kỹ thuật.',
        'BICEPS': 'Tay trước giúp tăng lực kéo và đóng vai trò lớn trong các bài tập lưng. Khi phát triển tốt, bắp tay sẽ nổi rõ, tạo cảm giác khỏe và thẩm mỹ hơn. Tuy không phải nhóm cơ lớn nhưng rất dễ thấy khi mặc áo ngắn tay.',
        'TRICEPS': 'Tay sau chiếm khoảng 2/3 kích thước bắp tay, nên nếu muốn tay to thì phải tập kỹ phần này. Nó giúp tăng lực đẩy trong các bài như ngực và vai, đồng thời làm cánh tay trông dày và chắc hơn.',
        'ABS': 'Cơ bụng không chỉ để có múi mà còn là trung tâm giữ ổn định toàn bộ cơ thể (core). Nó giúp bạn giữ thăng bằng, hỗ trợ gần như tất cả các bài tập từ nhẹ đến nặng, và giảm nguy cơ đau lưng. Một core khỏe giúp tập nặng an toàn hơn.',
        'CARDIO': 'Cardio giúp tăng sức bền tim mạch, cải thiện hô hấp, đốt mỡ và giúp cơ thể khỏe lâu dài chứ không chỉ đẹp bên ngoài. Nó cũng hỗ trợ phục hồi và giúp bạn không bị “đuối” khi tập tạ.',
    }

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
        # Lấy lợi ích tương ứng, nếu không có thì để trống hoặc câu mặc định
        benefit_text = benefits_data.get(muscle_group, "Tập luyện nhóm cơ này giúp bạn có hình thể cân đối và khỏe mạnh.")
    else:
        exercises = Exercise.objects.all().order_by('-created_at')
        current_name = "Tất cả bài tập"
        benefit_text = "Khám phá kho bài tập đa dạng để xây dựng lộ trình tập luyện toàn diện cho bản thân."

    return render(request, 'exercises/exercise_list.html', {
        'exercises': exercises,
        'current_name': current_name,
        'benefit_text': benefit_text  # Gửi biến này sang HTML
    })





def exercise_detail(request, pk):
    # 1. Lấy bài tập hiện tại khách đang xem
    exercise = get_object_or_404(Exercise, pk=pk)

    # 2. LẤY CÁC BÀI TẬP CÙNG NHÓM CƠ (Đây là đoạn quan trọng nhất)
    # Lọc những bài có cùng muscle_group, nhưng phải loại trừ bài đang xem ra (exclude pk=pk)
    related_exercises = Exercise.objects.filter(
        muscle_group=exercise.muscle_group
    ).exclude(pk=pk)[:4]  # Lấy tối đa 4 bài thôi cho đẹp giao diện

    context = {
        'exercise': exercise,
        'related_exercises': related_exercises,  # PHẢI CÓ DÒNG NÀY thì HTML mới thấy dữ liệu
    }
    return render(request, 'exercises/exercise_detail.html', context)


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
        return redirect('store:checkout') # Sửa: Thêm store:
    return redirect('store:cart') # Sửa: Thêm store:


@login_required(login_url='login')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required(login_url='login')
def update_cart_item(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id)
    if item.cart.user != request.user:
        return redirect('store:cart') # Sửa: Thêm store: (và thêm return)

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
        return redirect('store:checkout') # Sửa: Thêm store:
    return redirect('store:cart') # Sửa: Thêm store:


@login_required(login_url='login')
def checkout_view(request):
    """Trang thanh toán"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    if cart.items.count() == 0:
        messages.warning(request, "Giỏ hàng đang trống!")
        return redirect('store:store') # Sửa: Thêm store:

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


@staff_member_required(login_url='login')
def manage_products(request):
    # --- 1. CHỐT CHẶN PHÂN QUYỀN (An toàn cho Djongo) ---
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'Kho' in user_groups):
        messages.error(request, "Bạn không có quyền quản lý Kho và Sản phẩm!")
        return redirect('store:admin_dashboard')

    # --- 2. XỬ LÝ LOGIC NHẬP HÀNG (POST) ---
    if request.method == 'POST' and 'restock' in request.POST:
        try:
            product_id = request.POST.get('product_id')
            add_quantity = int(request.POST.get('add_quantity', 0))

            if add_quantity > 0:
                product = get_object_or_404(Product, pk=product_id)
                product.stock += add_quantity
                product.save()
                messages.success(request,
                                 f"📦 Đã nhập thêm {add_quantity} sản phẩm cho '{product.name}'. Tồn kho hiện tại: {product.stock}")
            else:
                messages.error(request, "Số lượng nhập phải lớn hơn 0!")
        except ValueError:
            messages.error(request, "Vui lòng nhập một số hợp lệ!")
        return redirect('store:manage_products')

    # --- 3. XỬ LÝ HIỂN THỊ & TÌM KIẾM (GET) ---
    search_query = request.GET.get('search', '')

    # Lấy toàn bộ danh sách ra list (Né lỗi order_by/filter trực tiếp của Djongo trên MongoDB)
    all_products = list(Product.objects.all())

    # Sắp xếp mới nhất lên đầu bằng Python
    products = sorted(all_products, key=lambda x: x.id, reverse=True)

    # Nếu có từ khóa tìm kiếm, lọc bằng Python luôn cho "bất tử"
    if search_query:
        query = search_query.lower()
        products = [
            p for p in products
            if query in p.name.lower() or
               (p.category and query in p.get_category_display().lower())
        ]

    return render(request, 'store/manage_products.html', {
        'products': products,
        'search_query': search_query  # Trả lại để hiển thị trên ô input
    })


@staff_member_required(login_url='login')
def edit_product(request, pk):
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'Kho' in user_groups):
        messages.error(request, "Bạn không có quyền quản lý Kho và Sản phẩm!")
        return redirect('store:admin_dashboard')
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
            return redirect('store:manage_products') # Sửa: Thêm store:
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form, 'product': product})


@staff_member_required(login_url='login')
def add_product(request):
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'Kho' in user_groups):
        messages.error(request, "Bạn không có quyền quản lý Kho và Sản phẩm!")
        return redirect('store:admin_dashboard')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            if 'detail_images' in request.FILES:
                images = request.FILES.getlist('detail_images')
                for img in images:
                    ProductImage.objects.create(product=product, image=img)
            messages.success(request, "Thêm sản phẩm thành công!")
            return redirect('store:manage_products') # Sửa: Thêm store:
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


@staff_member_required(login_url='login')
def delete_product(request, pk):
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'Kho' in user_groups):
        messages.error(request, "Bạn không có quyền quản lý Kho và Sản phẩm!")
        return redirect('store:admin_dashboard')
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, "Đã xóa sản phẩm!")
    return redirect('store:manage_products') # Sửa: Thêm store:


@staff_member_required(login_url='login')
def delete_image(request, img_id):
    img = get_object_or_404(ProductImage, id=img_id)
    p_id = img.product.id
    img.delete()
    messages.success(request, "Đã xóa ảnh phụ!")
    return redirect('store:edit_product', pk=p_id) # Sửa: Thêm store:


# ================= QUẢN LÝ BÀI TẬP (ADMIN) =================

@staff_member_required(login_url='login')
def manage_exercises(request):
    # CHỐT CHẶN PHÂN QUYỀN (Dùng Python an toàn cho Djongo)
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'PT' in user_groups):
        messages.error(request, "Bạn không có quyền chỉnh sửa Bài tập!")
        return redirect('store:admin_dashboard')

    # Lấy từ khóa từ ô tìm kiếm
    search_query = request.GET.get('search', '')

    # Lấy toàn bộ danh sách bài tập ra list (Fix lỗi Djongo)
    exercises_list = list(Exercise.objects.all().order_by('-id'))

    # Nếu có từ khóa, dùng Python để lọc (Tránh lỗi filter của MongoDB)
    if search_query:
        search_query = search_query.lower()
        exercises_list = [
            e for e in exercises_list
            if search_query in e.name.lower() or
               search_query in e.get_muscle_group_display().lower()
        ]

    return render(request, 'exercises/manage_exercises.html', {'exercises': exercises_list})


@staff_member_required(login_url='login')
def add_exercise(request):
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'PT' in user_groups):
        messages.error(request, "Bạn không có quyền chỉnh sửa Bài tập!")
        return redirect('store:admin_dashboard')
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm bài tập thành công!')
            return redirect('store:manage_exercises') # Sửa: Thêm store:
    else:
        form = ExerciseForm()
    return render(request, 'exercises/add_exercise.html', {'form': form})


@staff_member_required(login_url='login')
def delete_exercise(request, pk):
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'PT' in user_groups):
        messages.error(request, "Bạn không có quyền chỉnh sửa Bài tập!")
        return redirect('store:admin_dashboard')
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.delete()
    messages.success(request, 'Đã xóa bài tập!')
    return redirect('store:manage_exercises') # Sửa: Thêm store:


@staff_member_required(login_url='login')
def manage_orders(request):
    # --- FIX LỖI DJONGO M2M: Dùng Python để kiểm tra quyền thay vì .exists() ---
    is_kho = False
    try:
        # Lấy tất cả tên nhóm của user hiện tại
        user_groups = [g.name for g in request.user.groups.all()]
        if 'Kho' in user_groups:
            is_kho = True
    except Exception:
        pass

    # CHỐT CHẶN BẢO MẬT
    if not (request.user.is_superuser or is_kho):
        messages.error(request, "Bạn không có quyền quản lý Kho và Đơn hàng!")
        return redirect('store:admin_dashboard')

    # --- PHẦN 1: XỬ LÝ CẬP NHẬT TRẠNG THÁI ---
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            cancel_reason = request.POST.get('cancel_reason')
            order = Order.objects.get(id=order_id)
            old_status = order.status

            order.status = new_status
            if cancel_reason: order.cancel_reason = cancel_reason
            if new_status == 'COMPLETED': order.is_paid = True
            order.save()

            if old_status != new_status:
                # Logic tự động trừ tồn kho
                if new_status == 'SHIPPING' and old_status != 'SHIPPING':
                    for item in order.items.all():
                        product = item.product
                        product.stock -= item.quantity
                        if product.stock < 0:
                            product.stock = 0
                        product.save()

            messages.success(request, f"Đã cập nhật đơn hàng #{order_id}!")
        except Order.DoesNotExist:
            messages.error(request, "Không tìm thấy đơn hàng!")

    # --- PHẦN 2: CHUẨN BỊ DỮ LIỆU (ĐÃ FIX LỖI DJONGO BẰNG PYTHON) ---
    orders = []
    try:
        # Lấy tất cả Đơn hàng dạng list
        all_orders = list(Order.objects.all())
        # Dùng Python để sắp xếp
        orders = sorted(all_orders, key=lambda x: x.created_at, reverse=True)
    except Exception as e:
        print(f"Lỗi Djongo Order: {e}")

    # Dùng Python lọc trạng thái đơn
    completed_orders = [o for o in orders if o.status == 'COMPLETED']

    total_completed_count = len(completed_orders)
    pending_orders_count = len([o for o in orders if o.status == 'PENDING'])

    # 2.1 Tính TỔNG LỢI NHUẬN
    total_profit = 0
    for order in completed_orders:
        for item in order.items.all():
            p_price = item.product.price or 0
            p_import = item.product.import_price or 0
            total_profit += (p_price - p_import) * item.quantity

    # 2.2 Chuẩn bị dữ liệu LỢI NHUẬN chi tiết cho Biểu đồ
    chart_data = []
    for order in completed_orders:
        order_profit = 0
        for item in order.items.all():
            p_price = item.product.price or 0
            p_import = item.product.import_price or 0
            order_profit += (p_price - p_import) * item.quantity

        if order.created_at:
            chart_data.append({
                'date': order.created_at.strftime('%Y-%m-%d'),
                'month': order.created_at.strftime('%m/%Y'),
                'amount': float(order_profit)
            })

    # 2.3 Lấy danh sách các "Tháng/Năm" duy nhất
    unique_months = sorted(list(set(item['month'] for item in chart_data)),
                           key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)

    current_month_year = timezone.now().strftime('%m/%Y')
    if current_month_year not in unique_months:
        unique_months.insert(0, current_month_year)

    selected_month = request.GET.get('month', current_month_year)

    # --- PHẦN 3: TRẢ DỮ LIỆU ---
    return render(request, 'store/manage_orders.html', {
        'orders': orders,
        'total_revenue': total_profit,
        'total_completed_count': total_completed_count,
        'pending_orders_count': pending_orders_count,
        'unique_months': unique_months,
        'selected_month': selected_month,
        'chart_data_json': json.dumps(chart_data),
    })
@staff_member_required(login_url='login')
def edit_exercise(request, pk):
    user_groups = [g.name for g in request.user.groups.all()]
    if not (request.user.is_superuser or 'PT' in user_groups):
        messages.error(request, "Bạn không có quyền chỉnh sửa Bài tập!")
        return redirect('store:admin_dashboard')
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật bài tập '{exercise.name}'!")
            return redirect('store:manage_exercises')
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'exercises/edit_exercise.html', {'form': form, 'exercise': exercise})


@staff_member_required(login_url='login')
def manage_customers(request):
    if not request.user.is_superuser:
        messages.error(request, "Lỗi phân quyền: Chỉ Quản trị viên (Admin) mới được xem trang này!")
        return redirect('store:admin_dashboard')

    # --- XỬ LÝ KHI BẤM NÚT LƯU QUYỀN ---
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        try:
            target_user = User.objects.get(id=user_id)
            if target_user == request.user:
                messages.error(request, "Bạn không thể tự thay đổi quyền của chính mình!")
            else:
                if action == 'update_role':
                    role = request.POST.get('role')
                    target_user.groups.clear()  # Xóa hết phòng ban cũ

                    if role == 'khach_hang':
                        target_user.is_staff = False
                        messages.success(request,
                                         f"Đã thu hồi quyền của {target_user.username}, chuyển thành Khách hàng!")
                    else:
                        target_user.is_staff = True
                        # Tự động tạo Group nếu chưa có trong DB
                        group, _ = Group.objects.get_or_create(name=role)
                        target_user.groups.add(group)
                        role_name = "Quản lý Kho" if role == 'Kho' else "Quản lý Bài tập"
                        messages.success(request, f"Đã bổ nhiệm {target_user.username} làm {role_name}!")

                elif action == 'toggle_active':
                    target_user.is_active = not target_user.is_active
                    status = "Mở khóa" if target_user.is_active else "Khóa"
                    messages.success(request, f"Đã {status} tài khoản {target_user.username}!")

                target_user.save()
        except User.DoesNotExist:
            messages.error(request, "Không tìm thấy người dùng!")

        return redirect('store:manage_customers')

    # --- CHUẨN BỊ DỮ LIỆU HIỂN THỊ ---
    customers = []
    try:
        all_users = list(User.objects.all())
        for u in all_users:
            if not u.is_superuser:
                # Gắn nhãn để hiển thị HTML cho đẹp
                if u.is_staff:
                    group = u.groups.first()
                    if group and group.name == 'Kho':
                        u.role_display = "Quản lý Kho"
                        u.role_code = "Kho"
                    elif group and group.name == 'PT':
                        u.role_display = "Quản lý Bài tập"
                        u.role_code = "PT"
                    else:
                        u.role_display = "Nhân viên (Chưa phân ban)"
                        u.role_code = ""
                else:
                    u.role_display = "Khách hàng"
                    u.role_code = "khach_hang"
                customers.append(u)

        customers.sort(key=lambda x: x.date_joined, reverse=True)
    except Exception as e:
        print(f"Lỗi Djongo: {e}")

    return render(request, 'store/manage_customers.html', {'customers': customers})


@staff_member_required(login_url='login')
def admin_dashboard(request):
    from django.contrib.auth.models import User

    # 1. Số lượng Sản phẩm (Cái này MongoDB đếm được bình thường)
    total_products = Product.objects.count()

    # 2. FIX LỖI DJONGO: Đếm Khách hàng bằng Python
    total_customers = 0
    try:
        all_users = list(User.objects.all())
        total_customers = len([u for u in all_users if not u.is_staff])
    except Exception as e:
        print(f"Lỗi Djongo đếm User: {e}")

    # 3. FIX LỖI DJONGO: Đếm và Lọc Đơn hàng bằng Python
    pending_orders = 0
    completed_orders = []
    try:
        all_orders = list(Order.objects.all())
        pending_orders = len([o for o in all_orders if o.status == 'PENDING'])
        completed_orders = [o for o in all_orders if o.status == 'COMPLETED']
    except Exception as e:
        print(f"Lỗi Djongo lọc Order: {e}")

    # 4. Tính tổng lợi nhuận
    total_revenue = 0
    for order in completed_orders:
        for item in order.items.all():
            p_price = item.product.price or 0
            p_import = item.product.import_price or 0
            total_revenue += (p_price - p_import) * item.quantity

    return render(request, 'core/dashboard.html', {
        'total_products': total_products,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
    })


from django.http import JsonResponse

def exercise_autocomplete(request):
    query = request.GET.get('term', '')  # 'term' là từ khóa từ ô Search gửi qua
    results = []

    if query:
        try:
            # 1. Tìm trong Bài tập (Exercise) - Lấy 5 cái
            ex_qs = Exercise.objects.filter(name__icontains=query)[:5]

            # 2. Tìm trong Sản phẩm (Product) - Lấy 5 cái
            pr_qs = Product.objects.filter(name__icontains=query)[:5]

            # 3. Gói dữ liệu Bài tập (Gắn thêm link trang chi tiết và icon)
            for e in ex_qs:
                results.append({
                    'label': f"💪 {e.name}",        # Hiện ra có icon bắp tay cho ngầu
                    'value': e.name,               # Chữ điền vào ô tìm kiếm
                    'url': f"/store/exercise-detail/{e.id}/"    # Link bay thẳng tới trang chi tiết bài tập
                })

            # 4. Gói dữ liệu Sản phẩm (Gắn thêm link mua hàng và icon)
            for p in pr_qs:
                results.append({
                    'label': f"📦 {p.name}",        # Hiện ra có icon hộp hàng
                    'value': p.name,               # Chữ điền vào ô tìm kiếm
                    'url': f"/store/product/{p.id}/"     # Link bay thẳng tới trang chi tiết sản phẩm
                })

        except Exception as e:
            print(f"Lỗi Autocomplete: {e}")

    # Nhớ để safe=False vì mình đang trả về một List các Dictionary
    return JsonResponse(results, safe=False)

def api_get_all_products(request):
    """Cổng API cung cấp dữ liệu Sản phẩm cho AI Recommendation"""
    try:
        products = Product.objects.all()
        data = []
        for p in products:
            # Tạo đường dẫn (link) tới trang chi tiết sản phẩm
            # Chú ý: Đổi 'product_detail' thành tên name chuẩn trong urls.py của trang chi tiết
            product_url = f"/product/{p.id}/"

            data.append({
                'id': p.id,
                'name': p.name,
                'price': float(p.price) if p.price else 0,
                'category': p.get_category_display() if p.category else 'Khác',
                'stock': p.stock,
                'link': product_url,
                'image_url': p.image.url if p.image else ''
            })

        # Trả về chuỗi JSON
        return JsonResponse({
            'status': 'success',
            'total': len(data),
            'data': data
        }, safe=False)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})