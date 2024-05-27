import threading
from kubernetes import client, config

class LogAggregator:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.logs = []

    def fetch_logs(self, namespace, pod_name):
        log = self.v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
        self.logs.append(log)

    def run(self, namespace, pod_name):
        threading.Thread(target=self.fetch_logs, args=(namespace, pod_name)).start()

# Set up cron job for log eviction logic (not shown)
