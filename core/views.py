from django.shortcuts import render

from django.contrib.auth.decorators import login_required
@login_required(login_url='login')

def index(request):
    # Dữ liệu các nhóm cơ (Sau này có thể lấy từ Database)
    # Tạm thời dùng ảnh placeholder online để bạn thấy giao diện ngay
    muscle_groups = [
        {'name': 'Ngực', 'slug': 'nguc', 'img': 'images/nguc.webp'},
        {'name': 'Lưng / Xô', 'slug': 'lung', 'img': 'images/lung.png'},
        {'name': 'Tay Trước', 'slug': 'tay-truoc', 'img': 'images/tay_truoc.jpg'},
        {'name': 'Tay Sau', 'slug': 'tay-sau', 'img': 'images/tay_sau.jpg'},
        {'name': 'Bụng', 'slug': 'bung', 'img': 'images/bung.jpg'},
        {'name': 'Chân / Mông', 'slug': 'chan', 'img': 'images/chan.jpg'},
    ]

    context = {
        'muscle_groups': muscle_groups
    }
    return render(request, 'core/index.html', context)