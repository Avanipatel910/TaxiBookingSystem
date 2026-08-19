from django.contrib import admin
from django.urls import path
from core.views import admin_login, admin_logout, dashboard


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-login/', admin_login, name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
    path('dashboard/', dashboard, name='dashboard'),
]