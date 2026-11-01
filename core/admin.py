
from django.contrib import admin
from .models import Admin, User as CustomUser
from .models import Taxi, TaxiDetails, Booking


# Custom registered users
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'mobile', 'created_at')
    search_fields = ('name', 'email', 'mobile')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    exclude = ('password',)


# Admin accounts
@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')


# Taxi management
@admin.register(Taxi)
class TaxiAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'number',
        'type',
        'source',
        'destination',
        'price',
        'availability',
        'driver',
    )
    search_fields = ('number', 'source', 'destination')
    list_filter = ('availability', 'type')


# Taxi details management
@admin.register(TaxiDetails)
class TaxiDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'destination')
    search_fields = (
        'source',
        'destination',
        'driver__name',
        'driver__email',
    )
    list_filter = ('source', 'destination')


# Booking management
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'taxi', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = (
        'user__name',
        'user__email',
        'taxi__number',
    )
