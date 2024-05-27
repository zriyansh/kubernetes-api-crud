from django.utils import timezone
from django.shortcuts import get_object_or_404

from kubernetes import client, config

from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Deployment
from .serializers import DeploymentSerializer

import subprocess
import logging

class DeployView(views.APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        namespace = request.data.get('namespace')
        application_name = request.data.get('application_name')
        chart_name = request.data.get('chart_name')
        chart_version = request.data.get('chart_version')

        if not all([namespace, application_name, chart_name]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            config.load_kube_config()

            # Create a namespace
            v1 = client.CoreV1Api()
            namespace_body = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            try:
                v1.create_namespace(body=namespace_body)
            except client.exceptions.ApiException as e:
                if e.status == 409:
                    # means if Namespace already exists
                    pass
                else:
                    raise

            helm_repo_add_cmd = ['helm', 'repo', 'add', 'examples', 'https://helm.github.io/examples']
            result = subprocess.run(helm_repo_add_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return Response({
                    "error": "Helm repo add command failed",
                    "details": result.stderr
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # here, update Helm repositories
            helm_repo_update_cmd = ['helm', 'repo', 'update']
            result = subprocess.run(helm_repo_update_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return Response({
                    "error": "Helm repo update command failed",
                    "details": result.stderr
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # chart deploy
            helm_install_cmd = [
                'helm', 'install', application_name, f'examples/{chart_name}',
                '--namespace', namespace,
                # '--version', chart_version
            ]
            result = subprocess.run(helm_install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return Response({
                    "error": "Helm install command failed",
                    "details": result.stderr
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            health_status = self.check_health(namespace, application_name)

            deployment = Deployment.objects.create(
                namespace=namespace,
                application_name=application_name,
                deployed_at=timezone.now(),
                status=health_status
            )
            serializer = DeploymentSerializer(deployment)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def check_health(self, namespace, application_name):
        
        # some loic
        try:
            config.load_kube_config()
            v1 = client.CoreV1Api()
            pods = v1.list_namespaced_pod(namespace=namespace)
            for pod in pods.items:
                if application_name in pod.metadata.name:
                    if pod.status.phase != 'Running':
                        return 'Unhealthy'
            return 'Healthy'
        except Exception as e:
            return 'Unhealthy'


class DeploymentListView(generics.ListAPIView):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer

# config.load_kube_config()

class DeploymentLogsView(views.APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def get(self, request, id, *args, **kwargs):
        deployment = get_object_or_404(Deployment, id=id)
        namespace = deployment.namespace
        application_name = deployment.application_name

        try:
            config.load_kube_config()
            v1 = client.CoreV1Api()
            
            label_selector = f'app.kubernetes.io/instance={application_name}'
            pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
            
            if not pods.items:
                return Response({"logs": "", "debug": f"No pods found with the label {label_selector}"}, status=status.HTTP_200_OK)
            
            logs = ""
            for pod in pods.items:
                pod_logs = v1.read_namespaced_pod_log(name=pod.metadata.name, namespace=namespace)
                logs += f"Logs from pod {pod.metadata.name}:\n{pod_logs}\n\n"

            return Response({"logs": logs}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


logger = logging.getLogger(__name__)

class DeploymentDeleteView(views.APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def delete(self, request, id, *args, **kwargs):
        deployment = get_object_or_404(Deployment, id=id)
        namespace = deployment.namespace
        application_name = deployment.application_name

        try:
            config.load_kube_config()
            v1 = client.CoreV1Api()
            apps_v1 = client.AppsV1Api()

            label_selector = f'app.kubernetes.io/instance={application_name}'

            logger.info(f"Looking for deployments in namespace '{namespace}' with label selector '{label_selector}'")
            deployments = apps_v1.list_namespaced_deployment(namespace=namespace, label_selector=label_selector)
            if not deployments.items:
                logger.error("Deployment not found in Kubernetes")
                return Response({"error": "Deployment not found in Kubernetes"}, status=status.HTTP_404_NOT_FOUND)

            for dep in deployments.items:
                logger.info(f"Deleting deployment '{dep.metadata.name}' in namespace '{namespace}'")
                
                # Deleting the deployment
                apps_v1.delete_namespaced_deployment(name=dep.metadata.name, namespace=namespace)

                # Deleting the pods associated with the deployment
                pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
                for pod in pods.items:
                    logger.info(f"Deleting pod '{pod.metadata.name}' in namespace '{namespace}'")
                    v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)

            # logger.info(f"Deleting namespace '{namespace}'")
            # v1.delete_namespace(name=namespace)

            # to Remove the deployment from db
            logger.info(f"Deleting deployment record from the database with ID '{id}'")
            deployment.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except client.exceptions.ApiException as e:
            logger.error(f"Kubernetes API exception: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
