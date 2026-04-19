from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone          # Thêm cái này để lấy giờ hiện tại
from store.models import Coupon            # Thêm cái này để lấy Model Voucher
import requests
import json
from django.http import JsonResponse
from django.conf import settings


@login_required(login_url='login')
def index(request):
    # 1. Lấy TẤT CẢ Voucher ra trước (tránh dùng filter của Djongo để không bị lỗi SQL)
    try:
        # Lấy hết ra rồi dùng Python để lọc và cắt 3 cái đầu tiên
        all_coupons = Coupon.objects.all()
        active_vouchers = [v for v in all_coupons if v.active][:3]
    except Exception as e:
        print(f"Lỗi Database: {e}")
        active_vouchers = []

    # 2. Dữ liệu các nhóm cơ (Giữ nguyên của ông)
    muscle_groups = [
        {'name': 'Ngực', 'slug': 'nguc', 'img': 'images/nguc.webp'},
        {'name': 'Lưng / Xô', 'slug': 'lung', 'img': 'images/lung.png'},
        {'name': 'Tay Trước', 'slug': 'tay-truoc', 'img': 'images/tay_truoc.jpg'},
        {'name': 'Tay Sau', 'slug': 'tay-sau', 'img': 'images/tay_sau.jpg'},
        {'name': 'Bụng', 'slug': 'bung', 'img': 'images/bung.jpg'},
        {'name': 'Chân / Mông', 'slug': 'chan', 'img': 'images/chan.jpg'},
    ]

    context = {
        'muscle_groups': muscle_groups,
        'vouchers': active_vouchers
    }
    return render(request, 'core/index.html', context)

@login_required(login_url='login')
def ai_page(request):
    return render(request, 'core/ai.html')

