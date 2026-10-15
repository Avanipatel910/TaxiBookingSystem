from django.contrib import admin
from .models import Admin
from .models import Taxi

admin.site.register(Taxi)


@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')



