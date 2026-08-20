from django.contrib import admin
from django.urls import path

from core.views import (
    admin_login,
    admin_logout,
    admin_register,
    dashboard,
    admin_forgot_password,
    verify_otp,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('admin-login/', admin_login, name='admin_login'),

    path('admin-register/', admin_register, name='admin_register'),

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

    path('logout/', admin_logout, name='admin_logout'),

    path('dashboard/', dashboard, name='dashboard'),
]