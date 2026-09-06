from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from utils.base_model import BaseModel


class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    MOD = 'mod', 'Moderator'
    USER = 'user', 'User'

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff'):
            raise ValueError("Superuser musi mieć is_staff=True")
        if extra_fields.get('is_superuser'):
            raise ValueError("Superuser musi mieć is_superuser=True")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, PermissionsMixin, BaseModel):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MOD = 'mod', 'Moderator'
        USER = 'user', 'User'

    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    directional = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, default='', blank=True, null=True)
    avatar = models.CharField(max_length=200, default='', blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)


    def is_admin(self):
        return self.role == User.Role.ADMIN

    def is_moderator(self):
        return self.role == User.Role.MOD

    def __str__(self):
        return self.email

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
