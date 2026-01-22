from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(forms.ModelForm):
    # Thêm các trường nhập liệu
    full_name = forms.CharField(max_length=100, label="Họ và Tên")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    phone = forms.CharField(max_length=15, label="Số điện thoại")
    height = forms.FloatField(label="Chiều cao (cm)")
    weight = forms.FloatField(label="Cân nặng (kg)")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        # 1. Lưu User trước
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.first_name = self.cleaned_data['full_name'] # Lưu họ tên vào first_name
        if commit:
            user.save()
            # 2. Tạo Profile đi kèm User đó
            Profile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                height=self.cleaned_data['height'],
                weight=self.cleaned_data['weight']
            )
        return user