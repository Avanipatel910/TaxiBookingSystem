from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

import random


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


# =========================================================
# ADMIN FORGOT PASSWORD
# =========================================================

def admin_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        user = User.objects.filter(
            email=email,
            is_staff=True
        ).first()

        if not user:
            return render(
                request,
                'admin_forgot_password.html',
                {
                    'error': 'No admin account found with this email.'
                }
            )

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP information in session
        request.session['reset_otp'] = otp
        request.session['reset_email'] = email
        request.session['otp_verified'] = False

        try:
            send_mail(
                'Taxi Booking System - Password Reset OTP',

                f'''Hello {user.username},

Your password reset OTP is:

{otp}

This OTP is required to reset your admin password.

If you did not request a password reset, please ignore this email.

Regards,
Taxi Booking System
''',

                None,
                [email],

                fail_silently=False,
            )

        except Exception as e:
            print("EMAIL ERROR:", e)

            return render(
                request,
                'admin_forgot_password.html',
                {
                    'error': 'Unable to send OTP email. Please try again.'
                }
            )

        return redirect('verify_otp')

    return render(
        request,
        'admin_forgot_password.html'
    )


# =========================================================
# VERIFY OTP
# =========================================================

def verify_otp(request):

    # Make sure an OTP request actually exists
    if not request.session.get('reset_otp'):
        return redirect('admin_forgot_password')

    if request.method == 'POST':

        entered_otp = request.POST.get('otp', '').strip()
        saved_otp = request.session.get('reset_otp')

        if entered_otp == saved_otp:

            request.session['otp_verified'] = True

            return redirect('reset_password')

        return render(
            request,
            'verify_otp.html',
            {
                'error': 'Invalid OTP. Please try again.'
            }
        )

    return render(
        request,
        'verify_otp.html'
    )


# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password(request):

    # User must verify OTP first
    if not request.session.get('otp_verified'):
        return redirect('admin_forgot_password')

    email = request.session.get('reset_email')

    if not email:
        return redirect('admin_forgot_password')

    user = User.objects.filter(
        email=email,
        is_staff=True
    ).first()

    if not user:
        return redirect('admin_forgot_password')

    if request.method == 'POST':

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check empty fields
        if not password or not confirm_password:
            return render(
                request,
                'reset_password.html',
                {
                    'error': 'Both password fields are required.'
                }
            )

        # Check password match
        if password != confirm_password:
            return render(
                request,
                'reset_password.html',
                {
                    'error': 'Passwords do not match.'
                }
            )

        # Validate Django password rules
        try:
            validate_password(
                password,
                user
            )

        except ValidationError as e:
            return render(
                request,
                'reset_password.html',
                {
                    'error': ' '.join(e.messages)
                }
            )

        # Update password
        user.set_password(password)
        user.save()

        # Delete reset session data
        request.session.pop('reset_otp', None)
        request.session.pop('reset_email', None)
        request.session.pop('otp_verified', None)

        return render(
            request,
            'otp_verified.html',
            {
                'message': 'Password reset successfully!'
            }
        )

    return render(
        request,
        'reset_password.html'
    )


# =========================================================
# ADMIN REGISTER
# =========================================================

def admin_register(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        # Required fields
        if not username or not email or not password or not confirm_password:

            return render(
                request,
                'admin_register.html',
                {
                    'error': 'All fields are required.'
                }
            )

        # Password confirmation
        if password != confirm_password:

            return render(
                request,
                'admin_register.html',
                {
                    'error': 'Passwords do not match.'
                }
            )

        # Username already exists
        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'admin_register.html',
                {
                    'error': 'Username already exists.'
                }
            )

        # Email already exists
        if User.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                'admin_register.html',
                {
                    'error': 'Email already exists.'
                }
            )

        # Django password validation
        try:

            validate_password(
                password
            )

        except ValidationError as e:

            return render(
                request,
                'admin_register.html',
                {
                    'error': ' '.join(e.messages)
                }
            )

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Make user admin/staff
        user.is_staff = True
        user.save()

        return redirect('admin_login')

    return render(
        request,
        'admin_register.html'
    )