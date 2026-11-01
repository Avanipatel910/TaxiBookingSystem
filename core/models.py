
from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.hashers import make_password


class Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class AdminProfile(models.Model):
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )

    image = models.ImageField(
        upload_to='admin_profiles/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TaxiDetails(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.source} to {self.destination}"


class Driver(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    taxi_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    taxi_details = models.ForeignKey(
        TaxiDetails,
        on_delete=models.CASCADE,
        related_name='drivers',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Taxi(models.Model):
    number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=50)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='taxis'
    )

    def __str__(self):
        return f"{self.number} - {self.type}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    taxi = models.ForeignKey(
        Taxi,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"Booking #{self.id} - {self.status}"
