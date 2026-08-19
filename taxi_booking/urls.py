from django.contrib import admin
from django.urls import path
from core.views import home, admin_login

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("admin-login/", admin_login, name="admin_login"),
]