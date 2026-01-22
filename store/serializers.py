from rest_framework import serializers
from .models import Product
from .models import Exercise

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'image_url'] # Chọn trường muốn gửi đi

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ExerciseSerializer(serializers.ModelSerializer):
    muscle_group_display = serializers.CharField(source='get_muscle_group_display', read_only=True)

    class Meta:
        model = Exercise
        fields = ['id', 'title', 'muscle_group', 'muscle_group_display', 'video_file', 'description', 'created_at']