from rest_framework import serializers

class AIInputSerializer(serializers.Serializer):
    age = serializers.IntegerField()
    gender = serializers.CharField()
    height = serializers.FloatField()
    weight = serializers.FloatField()
    goal = serializers.CharField()
    activity_level = serializers.CharField(required=False, default="medium")
