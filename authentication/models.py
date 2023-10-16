from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('An email is required')
        if not password:
            raise ValueError('A password is required')
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=40, unique=True)
    display_name = models.CharField(max_length=40)
    email = models.EmailField(max_length=60, unique=True)
    password = models.CharField(max_length=128)

    date_joined = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS=['username','phone_number']
    
    # field to login with
    USERNAME_FIELD='email'
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username
