from django.contrib import admin
from .models import Admin


@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')