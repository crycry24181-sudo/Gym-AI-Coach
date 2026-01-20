from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm


# 1. Đăng ký
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Đăng ký xong tự động đăng nhập luôn
            return redirect('profile')  # Chuyển sang trang cá nhân
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# 2. Đăng nhập
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Về trang chủ
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


# 3. Đăng xuất
def logout_view(request):
    logout(request)
    return redirect('login')


# 4. Trang cá nhân (Xem BMI)
@login_required(login_url='login')
def profile_view(request):
    # Lấy thông tin User và Profile
    user = request.user
    try:
        profile = user.profile  # Lấy dữ liệu từ bảng Profile
    except:
        profile = None

    return render(request, 'users/profile.html', {'user': user, 'profile': profile})