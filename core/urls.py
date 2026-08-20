from django.contrib import admin
from django.urls import path
from core.views import (
    admin_login,
    admin_logout,
    admin_register,
    dashboard,
  
)
urlpatterns = [
    path('admin/', admin.site.urls),

    path('admin-login/', admin_login, name='admin_login'),

    path('admin-register/', admin_register, name='admin_register'),

  
    path('logout/', admin_logout, name='admin_logout'),

    path('dashboard/', dashboard, name='dashboard'),
]