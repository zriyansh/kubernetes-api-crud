from django.db import models
from django.utils import timezone

class Deployment(models.Model):
    namespace = models.CharField(max_length=100)
    application_name = models.CharField(max_length=100)
    deployed_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.application_name} in {self.namespace}"
