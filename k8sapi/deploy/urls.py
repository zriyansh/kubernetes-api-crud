from django.urls import path
from .views import DeployView, DeploymentListView, DeploymentLogsView, DeploymentDeleteView

urlpatterns = [
    path('', DeployView.as_view(), name='deploy'),
    path('deploy-list/', DeploymentListView.as_view(), name='deploy-list'),
    path('apps/<int:id>/logs/', DeploymentLogsView.as_view(), name='deployment-logs'),
    path('apps/<int:id>/', DeploymentDeleteView.as_view(), name='deployment-delete'),
]
