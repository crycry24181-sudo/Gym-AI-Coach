from django import forms
from .models import Product, Exercise
from .models import Coupon
from django.core.exceptions import ValidationError


# Widget tùy chỉnh để hỗ trợ chọn nhiều ảnh cùng lúc
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class ProductForm(forms.ModelForm):
    # Thêm một trường ảo (không nằm trong Model Product) để upload nhiều ảnh phụ (Gallery)
    detail_images = forms.FileField(
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}),
        required=False,
        label="Ảnh chi tiết sản phẩm (Chọn nhiều ảnh)"
    )

    class Meta:
        model = Product
        # ĐÃ THÊM: import_price và stock vào form
        fields = ['name', 'category', 'import_price', 'price', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên sản phẩm...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),

            # ĐÃ THÊM: Widget giao diện cho Giá nhập và Tồn kho
            'import_price': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Nhập giá vốn/giá nhập...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập giá bán...'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số lượng tồn kho...'}),

            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Mô tả chi tiết...'}),
        }
        labels = {
            'image': 'Ảnh đại diện chính (Hiện ở trang chủ)',
            'name': 'Tên sản phẩm',
            'category': 'Danh mục',

            # ĐÃ THÊM: Nhãn hiển thị cho Giá nhập và Tồn kho
            'import_price': 'Giá nhập (VNĐ)',
            'price': 'Giá bán lẻ (VNĐ)',
            'stock': 'Số lượng trong kho',

            'description': 'Mô tả sản phẩm'
        }


# --- ĐÂY LÀ PHẦN BẠN ĐANG THIẾU GÂY LỖI SẬP WEB ---
class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'muscle_group', 'description', 'image', 'video_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Đẩy ngực bằng tạ đòn...'}),
            'muscle_group': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Hướng dẫn tư thế, số set, số lần lặp...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(
                attrs={'class': 'form-control', 'placeholder': 'Link video YouTube hướng dẫn...'}),
        }
        labels = {
            'name': 'Tên bài tập',
            'muscle_group': 'Nhóm cơ tác động',
            'description': 'Hướng dẫn tập luyện',
            'image': 'Ảnh minh họa bài tập',
            'video_url': 'Link Video (YouTube)'
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'value', 'min_purchase', 'valid_from', 'valid_to', 'active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: NEWBIE50'}),
            'discount_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_discount_type'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_value', 'min': '0'}),
            'min_purchase': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # HÀM BẢO MẬT BACKEND: Kiểm tra dữ liệu trước khi lưu vào Database
    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        value = cleaned_data.get('value')

        # Nếu là phần trăm mà giá trị > 100 thì báo lỗi ngay
        if discount_type == 'PERCENTAGE' and value is not None and value > 100:
            self.add_error('value', 'Giá trị giảm theo phần trăm không được vượt quá 100%.')

        return cleaned_data