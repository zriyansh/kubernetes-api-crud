from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='authen_user_set',  
        blank=True,
        help_text=('.'),
        related_query_name='authen_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='authen_user_set',  
        blank=True,
        help_text='.',
        related_query_name='authen_user',
    )
