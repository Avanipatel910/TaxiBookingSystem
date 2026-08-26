from django.db import models
from django.contrib.auth.models import User
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
        User,
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


    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    mobile = models.CharField(
        max_length=15,
        unique=True
    )

    password = models.CharField(
        max_length=128
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(
                self.password
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name    


class Driver(models.Model):

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    license_number = models.CharField(
        max_length=50,
        unique=True
    )

    mobile = models.CharField(
        max_length=15
    )

    password = models.CharField(
        max_length=128
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(
                self.password
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name    