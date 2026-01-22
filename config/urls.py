from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Web
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('store/', include('store.urls')),

    # ✅ AI API (THÊM DÒNG NÀY)
    path('api/ai/', include('ai_coach.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
