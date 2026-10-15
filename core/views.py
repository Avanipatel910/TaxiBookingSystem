from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AdminUser
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.utils import timezone
from .forms import TaxiForm 
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.core.files import File
from datetime import datetime, timedelta
from .models import AdminProfile, User as CustomerUser, Driver

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


def user_register(request):

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip().lower()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not name or not email or not phone or not password or not confirm_password:

            return render(
                request,
                'auth/user_register.html',
                {
                    'error': 'All fields are required.',
                    'name': name,
                    'email': email,
                    'phone': phone,
                }
            )

        # -------------------------------------------------
        # PASSWORD MATCH
        # -------------------------------------------------

        if password != confirm_password:

            return render(
                request,
                'auth/user_register.html',
                {
                    'error': 'Passwords do not match.',
                    'name': name,
                    'email': email,
                    'phone': phone,
                }
            )

        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        if CustomerUser.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                'auth/user_register.html',
                {
                    'error': 'An account with this email already exists.',
                    'name': name,
                    'email': email,
                    'phone': phone,
                }
            )

        # -------------------------------------------------
        # MOBILE CHECK
        # -------------------------------------------------

        if CustomerUser.objects.filter(
            mobile=phone
        ).exists():

            return render(
                request,
                'auth/user_register.html',
                {
                    'error': 'An account with this phone number already exists.',
                    'name': name,
                    'email': email,
                    'phone': phone,
                }
            )

        # -------------------------------------------------
        # PASSWORD VALIDATION
        # -------------------------------------------------

        try:

            validate_password(password)

        except ValidationError as e:

            return render(
                request,
                'auth/user_register.html',
                {
                    'error': ' '.join(e.messages),
                    'name': name,
                    'email': email,
                    'phone': phone,
                }
            )

        # -------------------------------------------------
        # CREATE CUSTOMER
        # -------------------------------------------------

        CustomerUser.objects.create(
            name=name,
            email=email,
            mobile=phone,
            password=password
        )

        return redirect(
            'user_register_success'
        )

    return render(
        request,
        'auth/user_register.html'
    )

def user_register_success(request):
    return render(
        request,
        'auth/register_success.html'
    )

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            return render(request, 'auth/user_login.html', {
                'error': 'Email and password are required.',
                'email': email,
            })

        try:
            customer = CustomerUser.objects.get(email=email)
        except CustomerUser.DoesNotExist:
            return render(request, 'auth/user_login.html', {
                'error': 'Invalid email or password.',
                'email': email,
            })

        if not check_password(password, customer.password):
            return render(request, 'auth/user_login.html', {
                'error': 'Invalid email or password.',
                'email': email,
            })

        # Store logged-in customer in session
        request.session['customer_id'] = customer.id
        request.session['customer_name'] = customer.name
        request.session['customer_email'] = customer.email

        return redirect('user_dashboard')

    return render(request, 'auth/user_login.html')

def user_forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get('email', '').strip().lower()

        if not email:
            return render(request, 'auth/forgot_password.html', {
                'error': 'Please enter your email address.',
                'email': email,
            })

        try:
            customer = CustomerUser.objects.get(email=email)
        except CustomerUser.DoesNotExist:
            return render(request, 'auth/forgot_password.html', {
                'error': 'No account was found with this email address.',
                'email': email,
            })

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # OTP validity: 5 minutes
        otp_created_at = datetime.now()

        # Store OTP temporarily in session
        request.session['reset_otp'] = otp
        request.session['reset_email'] = email
        request.session['otp_created_at'] = otp_created_at.isoformat()
        request.session['otp_verified'] = False

        # Send OTP using Django console email backend
        send_mail(
            subject='Taxi Booking - Password Reset OTP',
            message=(
                f'Hello {customer.name},\n\n'
                f'Your password reset OTP is: {otp}\n\n'
                f'Please use this OTP to reset your password.\n\n'
                f'If you did not request a password reset, '
                f'please ignore this email.'
            ),
            from_email='noreply@taxibooking.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('user_verify_otp')

    return render(request, 'auth/forgot_password.html')

def user_verify_otp(request):

    if request.method == 'POST':

        entered_otp = request.POST.get('otp', '').strip()

        saved_otp = request.session.get('reset_otp')
        reset_email = request.session.get('reset_email')
        otp_created_at = request.session.get('otp_created_at')

        if not saved_otp or not reset_email or not otp_created_at:
            return render(request, 'auth/user_verify_otp.html', {
                'error': 'Your OTP session has expired. Please request a new OTP.'
            })

        if not entered_otp:
            return render(request, 'auth/user_verify_otp.html', {
                'error': 'Please enter the OTP.',
                'email': reset_email,
            })

        # Convert stored timestamp back to datetime
        try:
            created_time = datetime.fromisoformat(otp_created_at)
        except (ValueError, TypeError):
            request.session.pop('reset_otp', None)
            request.session.pop('otp_created_at', None)

            return render(request, 'auth/user_verify_otp.html', {
                'error': 'Invalid OTP session. Please request a new OTP.',
                'email': reset_email,
            })

        # Check whether OTP is older than 5 minutes
        if datetime.now() - created_time > timedelta(minutes=5):

            request.session.pop('reset_otp', None)
            request.session.pop('otp_created_at', None)

            return render(request, 'auth/user_verify_otp.html', {
                'error': 'Your OTP has expired. Please request a new OTP.',
                'email': reset_email,
            })

        # Check OTP
        if entered_otp != saved_otp:
            return render(request, 'auth/user_verify_otp.html', {
                'error': 'Invalid OTP. Please try again.',
                'email': reset_email,
            })

        # OTP verified successfully
        request.session['otp_verified'] = True

        return redirect('user_reset_password')

    return render(request, 'auth/user_verify_otp.html')

def user_reset_password(request):

    # Get password-reset session data
    reset_email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified', False)

    # User cannot access reset page without successful OTP verification
    if not reset_email or not otp_verified:
        return redirect('user_forgot_password')

    if request.method == 'POST':

        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validate password fields
        if not password or not confirm_password:
            return render(request, 'auth/user_reset_password.html', {
                'error': 'Both password fields are required.'
            })

        # Check password confirmation
        if password != confirm_password:
            return render(request, 'auth/user_reset_password.html', {
                'error': 'Passwords do not match.'
            })

        # Find customer account
        try:
            customer = CustomerUser.objects.get(email=reset_email)
        except CustomerUser.DoesNotExist:
            return redirect('user_forgot_password')

        # Update password
        customer.password = password
        customer.save()

        # Clear password reset session data
        request.session.pop('reset_otp', None)
        request.session.pop('reset_email', None)
        request.session.pop('otp_created_at', None)
        request.session.pop('otp_verified', None)

        # Send user back to login
        return redirect('user_login')

    return render(request, 'auth/user_reset_password.html')
def dashboard(request):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

    # Create profile automatically for old admin accounts
    AdminProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'admin/dashboard.html'
    )

def user_dashboard(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('user_login')

    customer = get_object_or_404(
        CustomerUser,
        id=customer_id
    )

    return render(request, 'user/dashboard.html', {
        'customer': customer
    })

def user_logout(request):
    request.session.flush()

    return redirect('user_login')

def admin_forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get(
            'email',
            ''
        ).strip()

        user = AdminUser.objects.filter(
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

        # -------------------------------------------------
        # GENERATE OTP
        # -------------------------------------------------

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        # -------------------------------------------------
        # SAVE OTP IN SESSION
        # -------------------------------------------------

        request.session['reset_otp'] = otp
        request.session['reset_email'] = email
        request.session['otp_verified'] = False

        # -------------------------------------------------
        # SEND EMAIL
        # -------------------------------------------------

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

                fail_silently=False
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

        return redirect(
            'verify_otp'
        )

    return render(
        request,
        'admin/auth/admin_forgot_password.html'
    )


def verify_otp(request):

    if not request.session.get(
        'reset_otp'
    ):

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

    if not request.session.get(
        'otp_verified'
    ):

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

    user = AdminUser.objects.filter(
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

        # Clear session
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

        return redirect(
            'dashboard'
        )

    # =====================================================
    # STEP 1: SEND OTP
    # =====================================================

    if request.method == 'POST' and request.POST.get(
        'action'
    ) == 'send_otp':

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

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not username or not email or not password or not confirm_password:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'All fields are required.',
                    'otp_stage':
                    False
                }
            )

        # -------------------------------------------------
        # USERNAME CHECK
        # -------------------------------------------------

        if AdminUser.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'Username already exists.',
                    'otp_stage':
                    False
                }
            )

        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        if AdminUser.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'Email already exists.',
                    'otp_stage':
                    False
                }
            )

        # -------------------------------------------------
        # PASSWORD MATCH
        # -------------------------------------------------

        if password != confirm_password:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'Passwords do not match.',
                    'otp_stage':
                    False
                }
            )

        # -------------------------------------------------
        # PASSWORD VALIDATION
        # -------------------------------------------------

        try:

            validate_password(
                password
            )

        except ValidationError as e:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    ' '.join(e.messages),
                    'otp_stage':
                    False
                }
            )

        # -------------------------------------------------
        # GENERATE OTP
        # -------------------------------------------------

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        # -------------------------------------------------
        # SAVE REGISTRATION DATA
        # -------------------------------------------------

        request.session[
            'registration_username'
        ] = username

        request.session[
            'registration_email'
        ] = email

        request.session[
            'registration_password'
        ] = password

        request.session[
            'registration_otp'
        ] = otp

        # -------------------------------------------------
        # SAVE IMAGE TEMPORARILY
        # -------------------------------------------------

        if profile_image:

            image_name = (
                'temp_admin_' +
                str(
                    random.randint(
                        100000,
                        999999
                    )
                ) +
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

        # -------------------------------------------------
        # SEND OTP EMAIL
        # -------------------------------------------------

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
                    'otp_stage':
                    False
                }
            )

        # -------------------------------------------------
        # SHOW OTP SECTION
        # -------------------------------------------------

        return render(
            request,
            'auth/admin_register.html',
            {
                'otp_stage':
                True,
                'email':
                email
            }
        )

    # =====================================================
    # STEP 2: VERIFY OTP
    # =====================================================

    if request.method == 'POST' and request.POST.get(
        'action'
    ) == 'verify_otp':

        entered_otp = request.POST.get(
            'otp',
            ''
        ).strip()

        saved_otp = request.session.get(
            'registration_otp'
        )

        # -------------------------------------------------
        # CHECK OTP EXISTS
        # -------------------------------------------------

        if not saved_otp:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'OTP session expired. Please register again.',
                    'otp_stage':
                    False
                }
            )

        # -------------------------------------------------
        # CHECK OTP
        # -------------------------------------------------

        if entered_otp != saved_otp:

            return render(
                request,
                'auth/admin_register.html',
                {
                    'error':
                    'Invalid OTP. Please check your email and try again.',
                    'otp_stage':
                    True,
                    'email':
                    request.session.get(
                        'registration_email'
                    )
                }
            )

        # -------------------------------------------------
        # GET REGISTRATION DATA
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CREATE ADMIN USER
        # -------------------------------------------------

        user = AdminUser.objects.create_user(

            username=username,

            email=email,

            password=password
        )

        # -------------------------------------------------
        # MAKE USER ADMIN
        # -------------------------------------------------

        user.is_staff = True

        user.save()

        # -------------------------------------------------
        # CREATE ADMIN PROFILE
        # -------------------------------------------------

        profile = AdminProfile.objects.create(
            user=user
        )

        # -------------------------------------------------
        # MOVE PROFILE IMAGE
        # -------------------------------------------------

        if image_path:

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

        # -------------------------------------------------
        # CLEAR REGISTRATION SESSION
        # -------------------------------------------------

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

        # -------------------------------------------------
        # REGISTRATION COMPLETE
        # -------------------------------------------------

        return redirect(
            'admin_login'
        )

    # =====================================================
    # NORMAL REGISTRATION PAGE
    # =====================================================

    return render(
        request,
        'auth/admin_register.html',
        {
            'otp_stage':
            False
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

        # -------------------------------------------------
        # GET REGISTRATION DATA
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CREATE ADMIN USER
        # -------------------------------------------------

        user = AdminUser.objects.create_user(

            username=username,

            email=email,

            password=password
        )

        # -------------------------------------------------
        # MAKE ADMIN
        # -------------------------------------------------

        user.is_staff = True

        user.save()

        # -------------------------------------------------
        # CREATE PROFILE
        # -------------------------------------------------

        profile = AdminProfile.objects.create(
            user=user
        )

        # -------------------------------------------------
        # MOVE IMAGE
        # -------------------------------------------------

        if image_path:

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

        # -------------------------------------------------
        # CLEAR SESSION
        # -------------------------------------------------

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

def driver_register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        license_number = request.POST.get('license_number', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        form_data = {
            'name': name,
            'email': email,
            'license_number': license_number,
            'phone': phone,
        }

        def show_error(message):
            return render(request, 'driver/driver_register.html', {
                'error': message,
                **form_data,
            })

        # 1. Required fields
        if not all([
            name, email, license_number, phone,
            password, confirm_password
        ]):
            return show_error('All fields are required.')

        # 2. Name validation
        if len(name) > 100:
            return show_error('Name must not exceed 100 characters.')

        # 3. Email validation
        try:
            validate_email(email)
        except ValidationError:
            return show_error('Please enter a valid email address.')

        # 4. Phone validation
        if not phone.isdigit() or not 7 <= len(phone) <= 15:
            return show_error(
                'Enter a valid phone number using 7 to 15 digits.'
            )

        # 5. License number validation
        if len(license_number) > 50:
            return show_error('License number must not exceed 50 characters.')

        # 6. Password confirmation
        if password != confirm_password:
            return show_error('Passwords do not match.')

        # 7. Password strength
        try:
            validate_password(password)
        except ValidationError as exc:
            return show_error(' '.join(exc.messages))

        # 8. Duplicate email check
        if Driver.objects.filter(email=email).exists():
            return show_error(
                'An account with this email already exists.'
            )

        # 9. Duplicate license check
        if Driver.objects.filter(
            license_number=license_number
        ).exists():
            return show_error(
                'This license number is already registered.'
            )

        # 10. Store the driver in the database
        Driver.objects.create(
            name=name,
            email=email,
            license_number=license_number,
            mobile=phone,
            password=password,
        )

        return render(request, 'driver/driver_register.html', {
            'success': 'Driver registration completed successfully.'
        })

    return render(request, 'driver/driver_register.html')



def driver_login(request):
    if request.session.get('driver_id'):
        return redirect('driver_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            return render(request, 'driver/driver_login.html', {
                'error': 'Please enter both email and password.',
                'email': email,
            })

        try:
            driver = Driver.objects.get(email=email)
        except Driver.DoesNotExist:
            return render(request, 'driver/driver_login.html', {
                'error': 'Invalid email or password.',
                'email': email,
            })

        if not check_password(password, driver.password):
            return render(request, 'driver/driver_login.html', {
                'error': 'Invalid email or password.',
                'email': email,
            })

        # Start a driver session after successful authentication.
        request.session.cycle_key()
        request.session['driver_id'] = driver.id
        request.session['driver_name'] = driver.name
        request.session['driver_email'] = driver.email

        return redirect('driver_dashboard')

    return render(request, 'driver/driver_login.html')


def driver_dashboard(request):
    driver_id = request.session.get('driver_id')

    if not driver_id:
        return redirect('driver_login')

    try:
        driver = Driver.objects.get(id=driver_id)
    except Driver.DoesNotExist:
        request.session.pop('driver_id', None)
        request.session.pop('driver_name', None)
        request.session.pop('driver_email', None)
        return redirect('driver_login')

    return render(
        request,
        'driver/driver_dashboard.html',
        {'driver': driver}
    )

def driver_logout(request):
    request.session.pop('driver_id', None)
    request.session.pop('driver_name', None)
    request.session.pop('driver_email', None)

    return redirect('driver_login')

def driver_forgot_password(request):
    if request.session.get('driver_id'):
        return redirect('driver_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            return render(request, 'driver/forgot_password.html', {
                'error': 'Please enter your registered email address.',
                'email': email,
            })

        try:
            driver = Driver.objects.get(email__iexact=email)
        except Driver.DoesNotExist:
            return render(request, 'driver/forgot_password.html', {
                'error': 'No driver account was found with that email.',
                'email': email,
            })

        otp = str(random.randint(100000, 999999))

        try:
            send_mail(
                'TaxiGo Driver Password Reset OTP',
                f'Hello {driver.name}, your password reset OTP is {otp}. '
                'It expires in 5 minutes. If you did not request this, '
                'please ignore this email.',
                None,
                [driver.email],
                fail_silently=False,
            )
        except Exception:
            return render(request, 'driver/forgot_password.html', {
                'error': 'Unable to send the OTP. Please try again.',
                'email': email,
            })

        request.session['driver_reset_otp'] = otp
        request.session['driver_reset_email'] = driver.email
        request.session['driver_otp_created_at'] = timezone.now().timestamp()
        request.session['driver_otp_verified'] = False

        return redirect('driver_verify_otp')

    return render(request, 'driver/forgot_password.html')


def driver_verify_otp(request):
    email = request.session.get('driver_reset_email')
    if not email:
        return redirect('driver_forgot_password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        stored_otp = request.session.get('driver_reset_otp')
        created_at = request.session.get('driver_otp_created_at')

        if not stored_otp or not created_at:
            return render(request, 'driver/verify_otp.html', {
                'error': 'Your OTP session has expired. Request a new OTP.'
            })

        if timezone.now().timestamp() - float(created_at) > 300:
            for key in (
                'driver_reset_otp',
                'driver_reset_email',
                'driver_otp_created_at',
                'driver_otp_verified',
            ):
                request.session.pop(key, None)

            return render(request, 'driver/forgot_password.html', {
                'error': 'Your OTP expired. Please request a new one.',
                'email': email,
            })

        if entered_otp != stored_otp:
            return render(request, 'driver/verify_otp.html', {
                'error': 'Invalid OTP. Please try again.'
            })

        request.session['driver_otp_verified'] = True
        return redirect('driver_reset_password')

    return render(request, 'driver/verify_otp.html')


def driver_reset_password(request):
    reset_email = request.session.get('driver_reset_email')
    otp_verified = request.session.get('driver_otp_verified')
    created_at = request.session.get('driver_otp_created_at')

    # Ensure the OTP was verified
    if not reset_email or not otp_verified or not created_at:
        messages.error(
            request,
            'Please verify your OTP before resetting your password.'
        )
        return redirect('driver_forgot_password')

    # Ensure the OTP has not expired
    if timezone.now().timestamp() - float(created_at) > 300:
        for key in (
            'driver_reset_otp',
            'driver_reset_email',
            'driver_otp_created_at',
            'driver_otp_verified',
        ):
            request.session.pop(key, None)

        messages.error(
            request,
            'Your OTP has expired. Please request a new one.'
        )
        return redirect('driver_forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not password or not confirm_password:
            return render(request, 'driver/reset_password.html', {
                'error': 'Please fill in both password fields.'
            })

        if password != confirm_password:
            return render(request, 'driver/reset_password.html', {
                'error': 'Passwords do not match.'
            })

        if len(password) < 8:
            return render(request, 'driver/reset_password.html', {
                'error': 'Password must contain at least 8 characters.'
            })

        try:
            driver = Driver.objects.get(email__iexact=reset_email)
        except Driver.DoesNotExist:
            for key in (
                'driver_reset_otp',
                'driver_reset_email',
                'driver_otp_created_at',
                'driver_otp_verified',
            ):
                request.session.pop(key, None)

            messages.error(
                request,
                'Driver account not found. Please try again.'
            )
            return redirect('driver_forgot_password')

        # Save the new password.
        # The Driver model's save() method hashes plain-text passwords.
        driver.password = password
        driver.save()

        # Clear password-reset session data
        for key in (
            'driver_reset_otp',
            'driver_reset_email',
            'driver_otp_created_at',
            'driver_otp_verified',
        ):
            request.session.pop(key, None)

        # Redirect to driver login with success message
        messages.success(
            request,
            'Your password has been reset successfully. '
            'Please log in with your new password.'
        )

        return redirect('driver_login')

    return render(request, 'driver/reset_password.html')

def drivers(request):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

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

        return redirect(
            'admin_login'
        )

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


# =========================================================
# DELETE DRIVER
# =========================================================

def delete_driver(request, driver_id):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

    driver = get_object_or_404(
        Driver,
        id=driver_id
    )

    if request.method == 'POST':

        driver.delete()

    return redirect(
        'drivers'
    )


# =========================================================
# CUSTOMERS / USERS
# =========================================================

def users(request):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

    search = request.GET.get(
        'search',
        ''
    ).strip()

    user_list = CustomerUser.objects.all().order_by(
        '-created_at'
    )

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


# =========================================================
# CUSTOMER DETAIL
# =========================================================

def user_detail(request, user_id):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

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


# =========================================================
# EDIT CUSTOMER
# =========================================================

def edit_user(request, user_id):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

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
                    'error':
                    'All fields are required.'
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
                    'error':
                    'Email already exists.'
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
                    'error':
                    'Mobile number already exists.'
                }
            )

        customer.name = name
        customer.email = email
        customer.mobile = mobile

        customer.save()

        return redirect(
            'users'
        )

    return render(
        request,
        'admin/users/edit_user.html',
        {
            'user': customer
        }
    )


# =========================================================
# DELETE CUSTOMER
# =========================================================

def delete_user(request, user_id):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

    customer = get_object_or_404(
        CustomerUser,
        id=user_id
    )

    if request.method == 'POST':

        customer.delete()

    return redirect(
        'users'
    )


# =========================================================
# BOOKINGS
# =========================================================

def bookings(request):

    if not request.user.is_authenticated or not request.user.is_staff:

        return redirect(
            'admin_login'
        )

    return render(
        request,
        'admin/bookings/bookings.html'
    )

def admin_add_taxi(request):
    # Use the same session-based check as your existing custom admin login.
    if not request.session.get('admin_id'):
        return redirect('admin_login')

    if request.method == 'POST':
        form = TaxiForm(request.POST)

        if form.is_valid():
            taxi = form.save()
            messages.success(
                request,
                f'Taxi {taxi.number} added successfully.'
            )
            return redirect('admin_add_taxi')
    else:
        form = TaxiForm(initial={'availability': True})

    return render(
        request,
        'admin/add_taxi.html',
        {'form': form}
    )
