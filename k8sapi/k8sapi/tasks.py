from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from deploy.models import Deployment

@shared_task
def check_stuck_deployments():
    stuck_time = timezone.now() - timedelta(minutes=5)
    stuck_deployments = Deployment.objects.filter(status='In_Progress', updated_at__lt=stuck_time)

    for deployment in stuck_deployments:
        deployment.status = 'Error'
        deployment.save()
