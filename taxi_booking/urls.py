from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from core.views import admin_login, admin_logout, admin_register, dashboard


urlpatterns = [
    path('admin/', admin.site.urls),

    path('admin-login/', admin_login, name='admin_login'),

    path('admin-register/', admin_register, name='admin_register'),

    path(
        'admin-forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='admin_forgot_password.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt',
            success_url='/admin-forgot-password/done/'
        ),
        name='admin_forgot_password'
    ),

    path(
        'admin-forgot-password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='admin_forgot_password_done.html'
        ),
        name='admin_password_reset_done'
    ),

    path(
        'admin-reset-password/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='admin_reset_password.html',
            success_url='/admin-reset-password/complete/'
        ),
        name='admin_password_reset_confirm'
    ),

    path(
        'admin-reset-password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='admin_reset_password_complete.html'
        ),
        name='admin_password_reset_complete'
    ),

    path('logout/', admin_logout, name='admin_logout'),

    path('dashboard/', dashboard, name='dashboard'),
]