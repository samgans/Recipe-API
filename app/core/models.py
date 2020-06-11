from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **kwargs):
        '''Create new user and save new user'''
        if not email:
            raise ValueError('User must have email')
        if not name:
            raise ValueError('User must have name')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        '''Creates new superuser'''

        superuser = self.create_user(email, name, password)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()

        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    '''User Model, changed the main USERNAME_FIELD from username to email'''
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]


class Tag(models.Model):
    '''Custom user tags for food'''
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
