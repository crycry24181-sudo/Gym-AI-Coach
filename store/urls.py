from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.store_view, name='store'),
    path('<int:pk>/', views.product_detail, name='product_detail'),

    # 👇 Thêm các đường dẫn mới 👇
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('add-product/', views.add_product, name='add_product'),
    path('manage-products/', views.manage_products, name='manage_products'), # Trang danh sách
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'), # Trang sửa
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'), # Trang xóa
    path('delete-image/<int:img_id>/', views.delete_image, name='delete_image'), # Xóa từng ảnh nhỏ
    path('api/products/', api_views.api_product_list, name='api_product_list'),
    path('quan-ly-bai-tap/', views.manage_exercises, name='manage_exercises'),
    path('them-bai-tap/', views.add_exercise, name='add_exercise'),
    path('xoa-bai-tap/<int:pk>/', views.delete_exercise, name='delete_exercise'),
# 1. Trang danh sách (Lọc theo nhóm cơ: CHEST, BACK...)
    path('bai-tap/<str:muscle_group>/', views.exercise_list, name='exercise_list'),

    # 2. Trang chi tiết bài tập (Xem cụ thể 1 bài theo ID)
    path('chi-tiet-bai-tap/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    path('api/exercises/', api_views.api_exercise_list, name='api_exercise_list'),
    path('api/exercises/<int:pk>/', api_views.api_exercise_detail, name='api_exercise_detail'),
]