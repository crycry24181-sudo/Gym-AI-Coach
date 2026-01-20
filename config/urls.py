from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Chuyển hướng trang chủ về app Core
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('store/', include('store.urls')),
]

# 👇 ĐOẠN NÀY LÀ QUAN TRỌNG NHẤT ĐỂ HIỆN ẢNH 👇
# Nó bảo Django: "Hãy mở thư mục static ra cho người dùng xem ảnh"
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)