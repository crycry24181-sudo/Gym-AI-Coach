from django.urls import path
from .views import AIRecommendAPIView
from .chat_views import AIChatAPIView

urlpatterns = [
    path("recommend/", AIRecommendAPIView.as_view()),
    path("chat/", AIChatAPIView.as_view()),
]
