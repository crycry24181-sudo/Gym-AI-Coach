from django.urls import path
from . import views

# DÒNG QUAN TRỌNG NHẤT: Khai báo namespace để fix lỗi 'store' is not a registered namespace
app_name = 'store'

urlpatterns = [
    # ===== TRANG CHỦ & CHI TIẾT SẢN PHẨM =====
    path('', views.store_view, name='store'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('manage-customers/', views.manage_customers, name='manage_customers'),
    path('erp/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ===== GIỎ HÀNG & THANH TOÁN =====
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),

    # ===== QUẢN TRỊ ĐƠN HÀNG & SẢN PHẨM (ADMIN) =====
    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('manage-products/', views.manage_products, name='manage_products'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('delete-image/<int:img_id>/', views.delete_image, name='delete_image'),

    # ===== QUẢN LÝ BÀI TẬP (ADMIN) =====
    path('manage-exercises/', views.manage_exercises, name='manage_exercises'),
    path('add-exercise/', views.add_exercise, name='add_exercise'),
    path('delete-exercise/<int:pk>/', views.delete_exercise, name='delete_exercise'),

    # ===== TRANG BÀI TẬP (USER - KHÁCH XEM) =====
    path('exercises/', views.exercise_list, name='exercise_list'), # Xem tất cả
    path('exercises/category/<str:muscle_group>/', views.exercise_list, name='exercise_list_by_group'), # Lọc theo nhóm cơ
    path('exercise-detail/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    path('manage-exercises/edit/<int:pk>/', views.edit_exercise, name='edit_exercise'),
    path('exercise-autocomplete/', views.exercise_autocomplete, name='exercise_autocomplete'),
    path('api/v1/products/', views.api_get_all_products, name='api_get_all_products'),
]
