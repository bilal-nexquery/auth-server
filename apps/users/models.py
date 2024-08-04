from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.users.managers import MyUserManager
from config import settings


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True, null=False, blank=False
    )
    username = models.CharField(max_length=255, unique=True, null=False, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_social = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class ResetPassword(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False
    )
    token = models.CharField(max_length=255, unique=True, null=False, blank=False)
    is_blacklisted = models.BooleanField(default=False)
    created_or_updated_at = models.DateTimeField(null=False, blank=False)
    expires_at = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return self.token
