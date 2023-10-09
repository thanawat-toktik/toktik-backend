from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, display_name, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            username=username, display_name=display_name, email=email, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, display_name, email, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, display_name, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=40)
    email = models.EmailField(max_length=60, unique=True)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username", "display_name", "email", "password"]

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        # Hash and set the user's password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        # Check if the provided password matches the stored hashed password
        return check_password(raw_password, self.password)
