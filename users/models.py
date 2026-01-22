from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True, blank=True)
    height = models.FloatField(help_text="Chiều cao tính bằng cm")
    weight = models.FloatField(help_text="Cân nặng tính bằng kg")

    def __str__(self):
        return f"Hồ sơ của {self.user.username}"

    # Hàm tính BMI tự động
    @property
    def bmi(self):
        if self.height and self.weight:
            # BMI = Cân nặng (kg) / (Chiều cao (m) * Chiều cao (m))
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 2)
        return 0