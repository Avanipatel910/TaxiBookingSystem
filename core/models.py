from django.db import models
from django.contrib.auth.models import User


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