from django import forms
from .models import Product

# 👇 Tạo Widget tùy chỉnh kế thừa từ FileInput để hỗ trợ chọn nhiều tệp
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên sản phẩm'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập giá tiền'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}), # Ảnh đại diện chính
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'image': 'Ảnh đại diện chính'
        }

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'image', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên sản phẩm'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập giá tiền'}),
            # Ảnh đại diện chính (chỉ chọn 1 ảnh)
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

        labels = {
            'image': 'Ảnh đại diện (Hiện ngoài trang chủ)'
        }