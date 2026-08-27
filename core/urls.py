from django.urls import path
from core.views import (
    admin_login,
    admin_logout,
    admin_register,
    dashboard,
    admin_forgot_password,
    verify_otp,
    reset_password,
    verify_registration_otp,
    drivers,
    driver_detail,
    users,
    user_detail,
    edit_user,
    delete_user,
    bookings,
)


urlpatterns = [

    path(
        'admin-login/',
        admin_login,
        name='admin_login'
    ),

    path(
        'admin-register/',
        admin_register,
        name='admin_register'
    ),

    path(
        'verify-registration-otp/',
        verify_registration_otp,
        name='verify_registration_otp'
    ),

    path(
        'logout/',
        admin_logout,
        name='admin_logout'
    ),

    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),

    path(
        'admin-forgot-password/',
        admin_forgot_password,
        name='admin_forgot_password'
    ),

    path(
        'verify-otp/',
        verify_otp,
        name='verify_otp'
    ),

    path(
        'reset-password/',
        reset_password,
        name='reset_password'
    ),

    path(
        'drivers/',
        drivers,
        name='drivers'
    ),

    path(
    'drivers/<int:driver_id>/',
    driver_detail,
    name='driver_detail'
    ),

    path(
        'users/',
        users,
        name='users'
    ),
    path(
    'users/<int:user_id>/',
    user_detail,
    name='user_detail'
),
    path(
    'users/<int:user_id>/edit/',
    edit_user,
    name='edit_user'
    ),

    path(
        'users/<int:user_id>/delete/',
        delete_user,
        name='delete_user'
    ),
    path(
        'bookings/',
        bookings,
        name='bookings'
    ),
]