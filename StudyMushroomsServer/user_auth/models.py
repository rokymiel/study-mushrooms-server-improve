from django.contrib.gis.db import models

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class MyUserManager(BaseUserManager):
    def create_user(self, email='', username='', common_name='', password=None):
        if not email or not username or not password:
            raise ValueError('No email/username/password')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            is_staff=False
        )
        user.save(using=self._db)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username='', password=None):
        if not username or not password:
            raise ValueError('No email/username/password')

        user = self.model(
            username=username,
            is_staff=True
        )
        user.save(using=self._db)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=30, default="", unique=True)
    email = models.EmailField(unique=True)
    session_key = models.CharField(max_length=200, default="", blank=True, null=True)
    recovery_code = models.PositiveIntegerField(default=0)
    verified_by_code = models.BooleanField(default=False)
    objects = MyUserManager()
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_perms(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff
