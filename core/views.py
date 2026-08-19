
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Admin

from django.contrib.auth.models import User


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')

        return render(
            request,
            'admin_login.html',
            {'error': 'Invalid admin username or password.'}
        )

    return render(request, 'admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    return render(request, 'dashboard.html')



def admin_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not password:
            return render(
                request,
                'admin_register.html',
                {'error': 'Username and password are required.'}
            )

        if password != confirm_password:
            return render(
                request,
                'admin_register.html',
                {'error': 'Passwords do not match.'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'admin_register.html',
                {'error': 'Username already exists.'}
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        user.is_staff = True
        user.save()

        return redirect('admin_login')

    return render(request, 'admin_register.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(
                request,
                'admin_register.html',
                {'error': 'Passwords do not match.'}
            )

        if Admin.objects.filter(username=username).exists():
            return render(
                request,
                'admin_register.html',
                {'error': 'Username already exists.'}
            )

        if Admin.objects.filter(email=email).exists():
            return render(
                request,
                'admin_register.html',
                {'error': 'Email already exists.'}
            )

        Admin.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        return redirect('admin_login')

    return render(request, 'admin_register.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(
                request,
                'admin_register.html',
                {'error': 'Passwords do not match.'}
            )

        if Admin.objects.filter(username=username).exists():
            return render(
                request,
                'admin_register.html',
                {'error': 'Username already exists.'}
            )

        if Admin.objects.filter(email=email).exists():
            return render(
                request,
                'admin_register.html',
                {'error': 'Email already exists.'}
            )

        Admin.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        return redirect('admin_login')

    return render(request, 'admin_register.html')