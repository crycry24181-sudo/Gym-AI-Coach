from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from .models import Coupon
import json

# Import Models
from .models import Product, Exercise

# Import Serializers (Bộ chuyển đổi dữ liệu)
from .serializers import ProductSerializer, ExerciseSerializer


# ================= API SẢN PHẨM =================

@api_view(['GET'])
def api_product_list(request):
    """API lấy danh sách tất cả sản phẩm"""
    products = Product.objects.all().order_by('-id')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# ================= API BÀI TẬP (GYM) =================

@api_view(['GET'])
def api_exercise_list(request):
    """
    API lấy danh sách bài tập.
    Có thể lọc theo nhóm cơ bằng cách thêm ?muscle=CHEST
    """
    muscle = request.GET.get('muscle')

    if muscle:
        # Nếu có tham số lọc (VD: ?muscle=CHEST)
        exercises = Exercise.objects.filter(muscle_group=muscle).order_by('-created_at')
    else:
        # Lấy tất cả nếu không lọc
        exercises = Exercise.objects.all().order_by('-created_at')

    serializer = ExerciseSerializer(exercises, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_exercise_detail(request, pk):
    """API xem chi tiết 1 bài tập theo ID"""
    try:
        exercise = Exercise.objects.get(pk=pk)
    except Exercise.DoesNotExist:
        return Response({'error': 'Không tìm thấy bài tập'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExerciseSerializer(exercise)
    return Response(serializer.data)


