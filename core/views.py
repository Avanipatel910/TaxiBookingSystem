from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordResetView
import random
from django.core.mail import send_mail


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


def admin_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = User.objects.filter(
            email=email,
            is_staff=True
        ).first()

        if user:
            otp = str(random.randint(100000, 999999))

            request.session['reset_otp'] = otp
            request.session['reset_email'] = email

            send_mail(
                'Admin Password Reset OTP',
                f'Your password reset OTP is: {otp}',
                'admin@example.com',
                [email],
                fail_silently=False,
            )

            return redirect('verify_otp')

        return render(
            request,
            'admin_forgot_password.html',
            {'error': 'No admin account found with this email.'}
        )

    return render(request, 'admin_forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('reset_otp')

        if entered_otp == saved_otp:
            request.session['otp_verified'] = True

            return render(
                request,
                'otp_verified.html',
                {'message': 'OTP verified successfully.'}
            )

        return render(
            request,
            'verify_otp.html',
            {'error': 'Invalid OTP.'}
        )

    return render(request, 'verify_otp.html')

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