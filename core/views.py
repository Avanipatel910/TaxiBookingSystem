from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


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