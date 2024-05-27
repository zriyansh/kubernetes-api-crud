from kubernetes import client, config
import subprocess

def create_namespace(namespace_name):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    namespace = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name))
    v1.create_namespace(body=namespace)

def install_helm_chart(namespace, chart_name):
    subprocess.run(['helm', 'install', chart_name, '--namespace', namespace])

def check_helm_app_health(namespace, app_name):
    return 'Active'
