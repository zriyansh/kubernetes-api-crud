from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='authen_user_set',  
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        related_query_name='authen_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='authen_user_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='authen_user',
    )
