from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from .models import AdminProfile, User as CustomerUser,Driver
import random
from django.shortcuts import render, redirect, get_object_or_404
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
            'auth/admin_login.html',
            {
                'error': 'Invalid admin username or password.'
            }
        )

    return render(
        request,
        'auth/admin_login.html'
    )


def admin_logout(request):

    logout(request)

    return redirect('admin_login')


def dashboard(request):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    # Create profile automatically for old admin accounts
    AdminProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'admin/dashboard.html'
    )


def admin_forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get(
            'email',
            ''
        ).strip()

        user = User.objects.filter(
            email=email,
            is_staff=True
        ).first()

        if not user:

            return render(
                request,
                'admin/auth/admin_forgot_password.html',
                {
                    'error':
                    'No admin account found with this email.'
                }
            )

        # Generate 6 digit OTP
        otp = str(
            random.randint(
                100000,
                999999
            )
        )

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

            print(
                "EMAIL ERROR:",
                e
            )

            return render(
                request,
                'admin/auth/admin_forgot_password.html',
                {
                    'error':
                    'Unable to send OTP email. Please try again.'
                }
            )

        return redirect('verify_otp')

    return render(
        request,
        'admin/auth/admin_forgot_password.html'
    )


def verify_otp(request):

    if not request.session.get('reset_otp'):

        return redirect(
            'admin_forgot_password'
        )

    if request.method == 'POST':

        entered_otp = request.POST.get(
            'otp',
            ''
        ).strip()

        saved_otp = request.session.get(
            'reset_otp'
        )

        if entered_otp == saved_otp:

            request.session['otp_verified'] = True

            return redirect(
                'reset_password'
            )

        return render(
            request,
            'admin/auth/verify_otp.html',
            {
                'error':
                'Invalid OTP. Please try again.'
            }
        )

    return render(
        request,
        'admin/auth/verify_otp.html'
    )


def reset_password(request):

    if not request.session.get('otp_verified'):

        return redirect(
            'admin_forgot_password'
        )

    email = request.session.get(
        'reset_email'
    )

    if not email:

        return redirect(
            'admin_forgot_password'
        )

    user = User.objects.filter(
        email=email,
        is_staff=True
    ).first()

    if not user:

        return redirect(
            'admin_forgot_password'
        )

    if request.method == 'POST':

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        if not password or not confirm_password:

            return render(
                request,
                'admin/auth/reset_password.html',
                {
                    'error':
                    'Both password fields are required.'
                }
            )

        if password != confirm_password:

            return render(
                request,
                'admin/auth/reset_password.html',
                {
                    'error':
                    'Passwords do not match.'
                }
            )

        try:

            validate_password(
                password,
                user
            )

        except ValidationError as e:

            return render(
                request,
                'admin/auth/reset_password.html',
                {
                    'error':
                    ' '.join(e.messages)
                }
            )

        user.set_password(
            password
        )

        user.save()

        request.session.pop(
            'reset_otp',
            None
        )

        request.session.pop(
            'reset_email',
            None
        )

        request.session.pop(
            'otp_verified',
            None
        )

        return render(
            request,
            'admin/auth/otp_verified.html',
            {
                'message':
                'Password reset successfully!'
            }
        )

    return render(
        request,
        'admin/auth/reset_password.html'
    )


def admin_register(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    # =========================================================
    # STEP 1: SEND OTP
    # =========================================================

    if request.method == 'POST' and request.POST.get('action') == 'send_otp':

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

        profile_image = request.FILES.get(
            'profile_image'
        )

        # =====================================================
        # REQUIRED FIELDS
        # =====================================================

        if not username or not email or not password or not confirm_password:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error': 'All fields are required.',
                    'otp_stage': False
                }
            )

        # =====================================================
        # USERNAME CHECK
        # =====================================================

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error': 'Username already exists.',
                    'otp_stage': False
                }
            )

        # =====================================================
        # EMAIL CHECK
        # =====================================================

        if User.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error': 'Email already exists.',
                    'otp_stage': False
                }
            )

        # =====================================================
        # PASSWORD MATCH
        # =====================================================

        if password != confirm_password:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error': 'Passwords do not match.',
                    'otp_stage': False
                }
            )

        # =====================================================
        # PASSWORD VALIDATION
        # =====================================================

        try:

            validate_password(password)

        except ValidationError as e:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error': ' '.join(e.messages),
                    'otp_stage': False
                }
            )

        # =====================================================
        # GENERATE OTP
        # =====================================================

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        # =====================================================
        # SAVE REGISTRATION DATA IN SESSION
        # =====================================================

        request.session['registration_username'] = username

        request.session['registration_email'] = email

        request.session['registration_password'] = password

        request.session['registration_otp'] = otp

        # =====================================================
        # SAVE IMAGE TEMPORARILY
        # =====================================================

        if profile_image:

            from django.core.files.storage import default_storage

            image_name = (
                'temp_admin_' +
                str(random.randint(100000, 999999)) +
                '_' +
                profile_image.name
            )

            saved_path = default_storage.save(
                'temp/' + image_name,
                profile_image
            )

            request.session[
                'registration_image_path'
            ] = saved_path

        else:

            request.session[
                'registration_image_path'
            ] = ''

        # =====================================================
        # SEND OTP EMAIL
        # =====================================================

        try:

            send_mail(

                'Taxi Booking System - Admin Registration OTP',

                f'''Hello {username},

Your Taxi Booking System admin registration OTP is:

{otp}

Enter this OTP on the registration page to complete your registration.

If you did not request this registration, please ignore this email.

Regards,
Taxi Booking System
''',

                None,

                [email],

                fail_silently=False
            )

        except Exception as e:

            print(
                "REGISTRATION EMAIL ERROR:",
                e
            )

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'Unable to send OTP email. Please try again.',
                    'otp_stage': False
                }
            )

        # =====================================================
        # SHOW OTP SECTION ON SAME PAGE
        # =====================================================

        return render(
            request,
            'auth/admin_register.html',
            {
                'otp_stage': True,
                'email': email
            }
        )


    # =========================================================
    # STEP 2: VERIFY OTP
    # =========================================================

    if request.method == 'POST' and request.POST.get('action') == 'verify_otp':

        entered_otp = request.POST.get(
            'otp',
            ''
        ).strip()

        saved_otp = request.session.get(
            'registration_otp'
        )

        # =====================================================
        # CHECK OTP EXISTS
        # =====================================================

        if not saved_otp:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'OTP session expired. Please register again.',
                    'otp_stage': False
                }
            )

        # =====================================================
        # CHECK OTP
        # =====================================================

        if entered_otp != saved_otp:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'Invalid OTP. Please check your email and try again.',
                    'otp_stage': True,
                    'email':
                    request.session.get(
                        'registration_email'
                    )
                }
            )

        # =====================================================
        # GET REGISTRATION DATA
        # =====================================================

        username = request.session.get(
            'registration_username'
        )

        email = request.session.get(
            'registration_email'
        )

        password = request.session.get(
            'registration_password'
        )

        image_path = request.session.get(
            'registration_image_path'
        )

        # =====================================================
        # CREATE USER
        # =====================================================

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password
        )

        # =====================================================
        # MAKE USER ADMIN
        # =====================================================

        user.is_staff = True

        user.save()

        # =====================================================
        # CREATE ADMIN PROFILE
        # =====================================================

        profile = AdminProfile.objects.create(
            user=user
        )

        # =====================================================
        # MOVE PROFILE IMAGE
        # =====================================================

        if image_path:

            from django.core.files.storage import default_storage
            from django.core.files import File

            if default_storage.exists(
                image_path
            ):

                with default_storage.open(
                    image_path,
                    'rb'
                ) as image_file:

                    profile.image.save(
                        image_path.split('/')[-1],
                        File(image_file),
                        save=True
                    )

                default_storage.delete(
                    image_path
                )

        # =====================================================
        # CLEAR REGISTRATION SESSION
        # =====================================================

        request.session.pop(
            'registration_username',
            None
        )

        request.session.pop(
            'registration_email',
            None
        )

        request.session.pop(
            'registration_password',
            None
        )

        request.session.pop(
            'registration_otp',
            None
        )

        request.session.pop(
            'registration_image_path',
            None
        )

        # =====================================================
        # REGISTRATION COMPLETE
        # =====================================================

        return redirect(
            'admin_login'
        )


    # =========================================================
    # NORMAL REGISTRATION PAGE
    # =========================================================

    return render(
        request,
        'auth/admin_register.html',
        {
            'otp_stage': False
        }
    )

def verify_registration_otp(request):


    otp = request.session.get(
        'registration_otp'
    )

    if not otp:

        return redirect(
            'admin_register'
        )

    if request.method == 'POST':

        entered_otp = request.POST.get(
            'otp',
            ''
        ).strip()

        if entered_otp != otp:

            return render(
                request,
                'auth/verify_registration_otp.html',
                {
                    'error':
                    'Invalid OTP. Please try again.',
                    'email':
                    request.session.get(
                        'registration_email'
                    )
                }
            )

        # =================================================
        # GET REGISTRATION DATA
        # =================================================

        username = request.session.get(
            'registration_username'
        )

        email = request.session.get(
            'registration_email'
        )

        password = request.session.get(
            'registration_password'
        )

        image_path = request.session.get(
            'registration_image_path'
        )

        # =================================================
        # CREATE USER
        # =================================================

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password
        )

        # =================================================
        # MAKE ADMIN
        # =================================================

        user.is_staff = True

        user.save()

    

        profile = AdminProfile.objects.create(
            user=user
        )



        if image_path:

            from django.core.files.storage import default_storage
            from django.core.files import File

            if default_storage.exists(
                image_path
            ):

                with default_storage.open(
                    image_path,
                    'rb'
                ) as image_file:

                    profile.image.save(
                        image_path.split('/')[-1],
                        File(image_file),
                        save=True
                    )

                default_storage.delete(
                    image_path
                )

   

        request.session.pop(
            'registration_username',
            None
        )

        request.session.pop(
            'registration_email',
            None
        )

        request.session.pop(
            'registration_password',
            None
        )

        request.session.pop(
            'registration_otp',
            None
        )

        request.session.pop(
            'registration_image_path',
            None
        )

        request.session.pop(
            'registration_image_name',
            None
        )

        

        return render(
            request,
            'auth/registration_success.html'
        )

    return render(
        request,
        'auth/verify_registration_otp.html',
        {
            'email':
            request.session.get(
                'registration_email'
            )
        }
    )

def drivers(request):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    search = request.GET.get(
        'search',
        ''
    ).strip()

    driver_list = Driver.objects.all().order_by(
        '-created_at'
    )

    if search:

        driver_list = driver_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        )

    return render(
        request,
        'admin/drivers/drivers.html',
        {
            'drivers': driver_list,
            'search': search
        }
    )


def driver_detail(request, driver_id):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    driver = get_object_or_404(
        Driver,
        id=driver_id
    )

    return render(
        request,
        'admin/drivers/driver_detail.html',
        {
            'driver': driver
        }
    )

def delete_driver(request, driver_id):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    driver = get_object_or_404(
        Driver,
        id=driver_id
    )

    if request.method == 'POST':

        driver.delete()

    return redirect('drivers')

def users(request):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    search = request.GET.get('search', '').strip()

    user_list = CustomerUser.objects.all().order_by('-created_at')

    if search:
        user_list = user_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        )

    return render(
        request,
        'admin/users/users.html',
        {
            'users': user_list,
            'search': search,
        }
    )

def user_detail(request, user_id):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    customer = get_object_or_404(
        CustomerUser,
        id=user_id
    )

    return render(
        request,
        'admin/users/user_detail.html',
        {
            'user': customer
        }
    )


def edit_user(request, user_id):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    customer = get_object_or_404(
        CustomerUser,
        id=user_id
    )

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        if not name or not email or not mobile:

            return render(
                request,
                'admin/users/edit_user.html',
                {
                    'user': customer,
                    'error': 'All fields are required.'
                }
            )

        if CustomerUser.objects.filter(
            email=email
        ).exclude(
            id=customer.id
        ).exists():

            return render(
                request,
                'admin/users/edit_user.html',
                {
                    'user': customer,
                    'error': 'Email already exists.'
                }
            )

        if CustomerUser.objects.filter(
            mobile=mobile
        ).exclude(
            id=customer.id
        ).exists():

            return render(
                request,
                'admin/users/edit_user.html',
                {
                    'user': customer,
                    'error': 'Mobile number already exists.'
                }
            )

        customer.name = name
        customer.email = email
        customer.mobile = mobile

        customer.save()

        return redirect('users')

    return render(
        request,
        'admin/users/edit_user.html',
        {
            'user': customer
        }
    )


def delete_user(request, user_id):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    customer = get_object_or_404(
        CustomerUser,
        id=user_id
    )

    if request.method == 'POST':
        customer.delete()

    return redirect('users')


def bookings(request):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    return render(
        request,
        'admin/bookings/bookings.html'
    )