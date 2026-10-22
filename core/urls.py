from django.urls import path
from .views import admin_add_taxi
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
    admin_add_taxi,
    admin_delete_taxi,
    admin_edit_taxi,
    admin_taxi_list,
    admin_view_taxi,
    taxi_search,
    driver_login,
    driver_dashboard,
    driver_logout,
    driver_forgot_password,
    driver_reset_password,
    driver_verify_otp,
    delete_driver,
    users,
    user_detail,
    edit_user,
    delete_user,
    bookings,
    user_register,
    user_register_success,
    user_login,
    user_forgot_password,
    user_verify_otp,
    user_reset_password,
    user_dashboard,
    user_logout,
    driver_register,
)


urlpatterns = [

    path(
    '',
    user_login,
    name='user_login'
),
path(
    'logout/',
    user_logout,
    name='user_logout'
),
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
        'admin-logout/',
        admin_logout,
        name='admin_logout'
    ),
    path('register/', user_register, name='user_register'),
    path(
    'register/success/',
    user_register_success,
    name='user_register_success'
),
path(
    'login/',
    user_login,
    name='user_login'
),
path('taxi-search/', taxi_search, name='taxi_search'),
path(
    'forgot-password/',
    user_forgot_password,
    name='user_forgot_password'
),
path('user-verify-otp/', user_verify_otp, name='user_verify_otp'),
path(
    'user-reset-password/',
    user_reset_password,
    name='user_reset_password'
),  
path(
    'dashboard/',
    user_dashboard,
    name='user_dashboard'
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
    'driver-register/',
    driver_register,
    name='driver_register'
),

path('driver-login/', driver_login, name='driver_login'),
path('driver-dashboard/', driver_dashboard, name='driver_dashboard'),
path('driver-logout/', driver_logout, name='driver_logout'),
path(
    'driver-forgot-password/',
    driver_forgot_password,
    name='driver_forgot_password'
),
path(
    'driver-verify-otp/',
    driver_verify_otp,
    name='driver_verify_otp'
),
path(
    'driver-reset-password/',
    driver_reset_password,
    name='driver_reset_password'
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
    'drivers/<int:driver_id>/delete/',
    delete_driver,
    name='delete_driver'
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
    path('admin/taxis/add/', admin_add_taxi, name='admin_add_taxi'),
    path('admin/taxis/', admin_taxi_list, name='admin_taxi_list'),
    path('admin/taxis/<int:taxi_id>/', admin_view_taxi, name='admin_view_taxi'),
    path('admin/taxis/<int:taxi_id>/edit/', admin_edit_taxi, name='admin_edit_taxi'),
    path('admin/taxis/<int:taxi_id>/delete/', admin_delete_taxi, name='admin_delete_taxi'),
]