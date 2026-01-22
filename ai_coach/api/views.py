from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ai_coach.logic import recommend_plan
from .serializers import AIInputSerializer


@method_decorator(csrf_exempt, name="dispatch")
class AIRecommendAPIView(APIView):
    permission_classes = [AllowAny]   # 🔥 QUAN TRỌNG

    def post(self, request):
        serializer = AIInputSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        result = recommend_plan(
            age=data["age"],
            gender=data["gender"],
            height=data["height"],
            weight=data["weight"],
            goal=data["goal"],
            activity_level=data.get("activity_level", "medium")
        )

        return Response(result, status=status.HTTP_200_OK)
