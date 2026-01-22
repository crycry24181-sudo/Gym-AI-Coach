from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # ✅ THÊM DÒNG NÀY
    path('ai/', views.ai_page, name='ai'),
]
