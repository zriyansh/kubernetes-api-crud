from django.utils import timezone
from django.shortcuts import get_object_or_404
from kubernetes import client, config
from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Deployment
from .serializers import DeploymentSerializer
import subprocess
import logging
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.db import transaction
import asyncio
import aiohttp
from kubernetes_asyncio import client as async_client, config as async_config
import time

logger = logging.getLogger(__name__)
class DeployView(views.APIView):
    permission_classes = (AllowAny,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        namespace = request.data.get('namespace')
        application_name = request.data.get('application_name')
        chart_link = request.data.get('chart_link')

        if not all([namespace, application_name, chart_link]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = async_to_sync(self.deploy)(
                namespace, application_name, chart_link
            )
            return result

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def deploy(self, namespace, application_name, chart_link):
        try:
            await async_config.load_kube_config()

            v1 = async_client.CoreV1Api()
            namespace_body = async_client.V1Namespace(
                metadata=async_client.V1ObjectMeta(name=namespace)
            )
            try:
                await v1.create_namespace(body=namespace_body)
            except async_client.exceptions.ApiException as e:
                if e.status == 409:
                    pass  # Namespace exist
                else:
                    raise

            helm_repo_update_cmd = ['helm', 'repo', 'update']
            result = await sync_to_async(subprocess.run)(helm_repo_update_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return Response({
                    "error": "Helm repo update command failed",
                    "details": result.stderr
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if await sync_to_async(Deployment.objects.filter(namespace=namespace).exists)():
                return Response({'error': 'Namespace already exists, make a unique one'})
            else:
                helm_install_cmd = [
                    'helm', 'install', application_name, chart_link,
                    '--namespace', namespace,
                ]
                result = await sync_to_async(subprocess.run)(helm_install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    return Response({
                        "error": "Helm install command failed",
                        "details": result.stderr
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                await self.broadcast_status(namespace, application_name, "In_Progress")

                time.sleep(10)  # Delay added for pods to be created ache se

                health_status = await self.check_health(namespace, application_name)

                deployment = await sync_to_async(Deployment.objects.create)(
                    namespace=namespace,
                    application_name=application_name,
                    deployed_at=timezone.now(),
                    status=health_status
                )

                await self.broadcast_status(namespace, application_name, health_status)

                serializer = DeploymentSerializer(deployment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def check_health(self, namespace, application_name):
        try:
            await async_config.load_kube_config()
            v1 = async_client.CoreV1Api()
            pods = await v1.list_namespaced_pod(namespace=namespace)
            for pod in pods.items:
                if application_name in pod.metadata.name:
                    if pod.status.phase != 'Running':
                        return 'Error'
            return 'Running'
        except Exception as e:
            return 'Error'

    async def broadcast_status(self, namespace, application_name, status):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "deployments",
            {
                "type": "send_status_update",
                "id": application_name,
                "status": status,
            }
        )


class DeploymentListView(generics.ListAPIView):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer

# config.load_kube_config()

class DeploymentLogsView(views.APIView):
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
                logger.debug(f"No pods found with the label {label_selector}")
                return Response({"logs": "", "debug": f"No pods found with the label {label_selector}"}, status=status.HTTP_200_OK)

            logs = ""
            for pod in pods.items:
                pod_logs = v1.read_namespaced_pod_log(name=pod.metadata.name, namespace=namespace)
                logs += f"Logs from pod {pod.metadata.name}:\n{pod_logs}\n\n"

            return Response({"logs": logs}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Log retrieval error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class DeploymentDeleteView(views.APIView):
    permission_classes = (AllowAny,)

    def delete(self, request, id, *args, **kwargs):
        return async_to_sync(self.delete_deployment)(request, id, *args, **kwargs)

    async def delete_deployment(self, request, id, *args, **kwargs):
        deployment = await sync_to_async(get_object_or_404)(Deployment, id=id)
        namespace = deployment.namespace
        application_name = deployment.application_name

        try:
            await sync_to_async(config.load_kube_config)()
            v1 = client.CoreV1Api()
            apps_v1 = client.AppsV1Api()

            label_selector = f'app.kubernetes.io/instance={application_name}'
            deployments = await sync_to_async(apps_v1.list_namespaced_deployment)(namespace=namespace, label_selector=label_selector)

            if not deployments.items:
                logger.error("Deployment not found in Kubernetes")
                return Response({"error": "Deployment not found in Kubernetes"}, status=status.HTTP_404_NOT_FOUND)

            tasks = [self.delete_deployment_and_pods(v1, apps_v1, dep, namespace, label_selector) for dep in deployments.items]
            await asyncio.gather(*tasks)

            # Remove the deployment from DB
            logger.info(f"Deleting deployment record from the database with ID '{id}'")
            await sync_to_async(deployment.delete)()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except client.exceptions.ApiException as e:
            logger.error(f"Kubernetes API exception: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def delete_deployment_and_pods(self, v1, apps_v1, deployment, namespace, label_selector):
        try:
            await asyncio.to_thread(apps_v1.delete_namespaced_deployment, name=deployment.metadata.name, namespace=namespace)
            pods = await asyncio.to_thread(v1.list_namespaced_pod, namespace=namespace, label_selector=label_selector)
            delete_pod_tasks = [asyncio.to_thread(v1.delete_namespaced_pod, name=pod.metadata.name, namespace=namespace) for pod in pods.items]
            await asyncio.gather(*delete_pod_tasks)
        except Exception as e:
            logger.error(f"Error deleting deployment or pods: {str(e)}")
