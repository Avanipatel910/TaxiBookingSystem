from django.contrib import admin
from .models import Admin
from .models import Taxi,TaxiDetails

admin.site.register(Taxi)


@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')

@admin.register(TaxiDetails)
class TaxiDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'destination', 'driver')
    search_fields = (
        'source',
        'destination',
        'driver__name',
        'driver__email',
    )
    list_filter = ('source', 'destination')

