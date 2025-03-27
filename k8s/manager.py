"""
Kubernetes deployment manager for FinancialMediator.
"""

import os
import time
from typing import Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from .config import (
    APP_NAME, NAMESPACE, ENV_VARS, POSTGRES_CONFIG,
    VOLUME_CONFIG, SERVICE_CONFIG, IMAGE_CONFIG, REPLICAS
)

class K8sManager:
    """
    Kubernetes deployment manager.
    Handles all Kubernetes operations for the application.
    """
    
    def __init__(self):
        """Initialize the Kubernetes manager."""
        self._init_k8s()
        
    def _init_k8s(self):
        """Initialize Kubernetes client."""
        try:
            config.load_kube_config()
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            print("Kubernetes client initialized successfully")
        except Exception as e:
            print(f"Error initializing Kubernetes client: {str(e)}")
            raise
    
    def create_namespace(self) -> bool:
        """
        Create namespace for the application.
        
        Returns:
            bool: True if namespace created successfully
        """
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=NAMESPACE)
            )
            self.v1.create_namespace(namespace)
            print(f"Namespace '{NAMESPACE}' created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # Namespace already exists
                print(f"Namespace '{NAMESPACE}' already exists")
                return True
            print(f"Error creating namespace: {str(e)}")
            return False
    
    def create_configmap(self) -> bool:
        """
        Create ConfigMap with environment variables.
        
        Returns:
            bool: True if ConfigMap created successfully
        """
        try:
            metadata = client.V1ObjectMeta(
                name=f"{APP_NAME}-config",
                namespace=NAMESPACE
            )
            configmap = client.V1ConfigMap(
                metadata=metadata,
                data=ENV_VARS
            )
            self.v1.create_namespaced_config_map(NAMESPACE, configmap)
            print(f"ConfigMap '{APP_NAME}-config' created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # ConfigMap already exists
                print(f"ConfigMap '{APP_NAME}-config' already exists")
                return True
            print(f"Error creating ConfigMap: {str(e)}")
            return False
    
    def create_postgres_pv(self) -> bool:
        """
        Create PersistentVolume for PostgreSQL.
        
        Returns:
            bool: True if PersistentVolume created successfully
        """
        try:
            metadata = client.V1ObjectMeta(
                name="postgres-pv",
                namespace=NAMESPACE
            )
            spec = client.V1PersistentVolumeSpec(
                capacity={"storage": POSTGRES_CONFIG["storage"]},
                access_modes=["ReadWriteOnce"],
                host_path=client.V1HostPathVolumeSource(
                    path=VOLUME_CONFIG["postgres_path"]
                )
            )
            pv = client.V1PersistentVolume(
                metadata=metadata,
                spec=spec
            )
            self.v1.create_persistent_volume(pv)
            print("PostgreSQL PersistentVolume created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # PV already exists
                print("PostgreSQL PersistentVolume already exists")
                return True
            print(f"Error creating PersistentVolume: {str(e)}")
            return False
    
    def create_postgres_pvc(self) -> bool:
        """
        Create PersistentVolumeClaim for PostgreSQL.
        
        Returns:
            bool: True if PersistentVolumeClaim created successfully
        """
        try:
            metadata = client.V1ObjectMeta(
                name="postgres-pvc",
                namespace=NAMESPACE
            )
            spec = client.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=client.V1ResourceRequirements(
                    requests={"storage": POSTGRES_CONFIG["storage"]}
                )
            )
            pvc = client.V1PersistentVolumeClaim(
                metadata=metadata,
                spec=spec
            )
            self.v1.create_namespaced_persistent_volume_claim(NAMESPACE, pvc)
            print("PostgreSQL PersistentVolumeClaim created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # PVC already exists
                print("PostgreSQL PersistentVolumeClaim already exists")
                return True
            print(f"Error creating PersistentVolumeClaim: {str(e)}")
            return False
    
    def create_postgres_deployment(self) -> bool:
        """
        Create PostgreSQL deployment.
        
        Returns:
            bool: True if deployment created successfully
        """
        try:
            metadata = client.V1ObjectMeta(
                name="postgres",
                namespace=NAMESPACE
            )
            spec = client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app": "postgres"}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": "postgres"}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="postgres",
                                image=IMAGE_CONFIG["postgres"],
                                ports=[
                                    client.V1ContainerPort(
                                        container_port=5432
                                    )
                                ],
                                env=[
                                    client.V1EnvVar(
                                        name="POSTGRES_DB",
                                        value=POSTGRES_CONFIG["db"]
                                    ),
                                    client.V1EnvVar(
                                        name="POSTGRES_USER",
                                        value=POSTGRES_CONFIG["user"]
                                    ),
                                    client.V1EnvVar(
                                        name="POSTGRES_PASSWORD",
                                        value=POSTGRES_CONFIG["password"]
                                    )
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="postgres-storage",
                                        mount_path="/var/lib/postgresql/data"
                                    )
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="postgres-storage",
                                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                    claim_name="postgres-pvc"
                                )
                            )
                        ]
                    )
                )
            )
            deployment = client.V1Deployment(
                metadata=metadata,
                spec=spec
            )
            self.apps_v1.create_namespaced_deployment(NAMESPACE, deployment)
            print("PostgreSQL deployment created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # Deployment already exists
                print("PostgreSQL deployment already exists")
                return True
            print(f"Error creating PostgreSQL deployment: {str(e)}")
            return False
    
    def create_postgres_service(self) -> bool:
        """
        Create PostgreSQL service.
        
        Returns:
            bool: True if service created successfully
        """
        try:
            metadata = client.V1ObjectMeta(
                name="postgres",
                namespace=NAMESPACE
            )
            spec = client.V1ServiceSpec(
                selector={"app": "postgres"},
                ports=[
                    client.V1ServicePort(
                        protocol="TCP",
                        port=5432,
                        target_port=5432
                    )
                ]
            )
            service = client.V1Service(
                metadata=metadata,
                spec=spec
            )
            self.v1.create_namespaced_service(NAMESPACE, service)
            print("PostgreSQL service created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # Service already exists
                print("PostgreSQL service already exists")
                return True
            print(f"Error creating PostgreSQL service: {str(e)}")
            return False
    
    def create_web_deployment(self) -> bool:
        """
        Create web application deployment.
        
        Returns:
            bool: True if deployment created successfully
        """
        try:
            metadata = client.V1ObjectMeta(
                name=APP_NAME,
                namespace=NAMESPACE
            )
            spec = client.V1DeploymentSpec(
                replicas=REPLICAS,
                selector=client.V1LabelSelector(
                    match_labels={"app": APP_NAME}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": APP_NAME}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="web",
                                image=IMAGE_CONFIG["web"],
                                command=["python", "manage.py", "runserver", "0.0.0.0:8000"],
                                ports=[
                                    client.V1ContainerPort(
                                        container_port=8000
                                    )
                                ],
                                env_from=[
                                    client.V1EnvFromSource(
                                        config_map_ref=client.V1ConfigMapEnvSource(
                                            name=f"{APP_NAME}-config"
                                        )
                                    )
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="code",
                                        mount_path="/app"
                                    )
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="code",
                                host_path=client.V1HostPathVolumeSource(
                                    path=VOLUME_CONFIG["host_path"]
                                )
                            )
                        ]
                    )
                )
            )
            deployment = client.V1Deployment(
                metadata=metadata,
                spec=spec
            )
            self.apps_v1.create_namespaced_deployment(NAMESPACE, deployment)
            print("Web deployment created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # Deployment already exists
                print("Web deployment already exists")
                return True
            print(f"Error creating web deployment: {str(e)}")
            return False
    
    def create_web_service(self) -> bool:
        """
        Create web application service.
        
        Returns:
            bool: True if service created successfully
        """
        try:
            metadata = client.V1ObjectMeta(
                name=APP_NAME,
                namespace=NAMESPACE
            )
            spec = client.V1ServiceSpec(
                selector={"app": APP_NAME},
                ports=[
                    client.V1ServicePort(
                        protocol="TCP",
                        port=SERVICE_CONFIG["port"],
                        target_port=SERVICE_CONFIG["target_port"]
                    )
                ],
                type=SERVICE_CONFIG["type"]
            )
            service = client.V1Service(
                metadata=metadata,
                spec=spec
            )
            self.v1.create_namespaced_service(NAMESPACE, service)
            print("Web service created successfully")
            return True
        except ApiException as e:
            if e.status == 409:  # Service already exists
                print("Web service already exists")
                return True
            print(f"Error creating web service: {str(e)}")
            return False
    
    def wait_for_postgres(self, timeout: int = 30) -> bool:
        """
        Wait for PostgreSQL to be ready.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if PostgreSQL is ready
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                pods = self.v1.list_namespaced_pod(
                    NAMESPACE,
                    label_selector="app=postgres"
                )
                for pod in pods.items:
                    if pod.status.phase == "Running":
                        return True
                time.sleep(2)
            except Exception as e:
                print(f"Error checking PostgreSQL status: {str(e)}")
                return False
        return False
    
    def get_service_url(self) -> str:
        """
        Get the URL where the application is running.
        
        Returns:
            str: URL of the application
        """
        try:
            service = self.v1.read_namespaced_service(
                name=APP_NAME,
                namespace=NAMESPACE
            )
            node_port = service.spec.ports[0].node_port
            minikube_ip = os.popen("minikube ip").read().strip()
            return f"http://{minikube_ip}:{node_port}"
        except Exception as e:
            print(f"Error getting service URL: {str(e)}")
            return ""
    
    def deploy(self) -> bool:
        """
        Deploy the entire application to Kubernetes.
        
        Returns:
            bool: True if deployment was successful
        """
        try:
            # Create namespace
            if not self.create_namespace():
                return False
            
            # Create ConfigMap
            if not self.create_configmap():
                return False
            
            # Create PostgreSQL resources
            if not self.create_postgres_pv():
                return False
            if not self.create_postgres_pvc():
                return False
            if not self.create_postgres_deployment():
                return False
            if not self.create_postgres_service():
                return False
            
            # Wait for PostgreSQL to be ready
            if not self.wait_for_postgres():
                print("PostgreSQL did not become ready in time")
                return False
            
            # Create web application resources
            if not self.create_web_deployment():
                return False
            if not self.create_web_service():
                return False
            
            # Get and print the application URL
            url = self.get_service_url()
            if url:
                print(f"\nApplication is running at: {url}")
                print(f"Admin interface: {url}/admin")
            
            return True
        except Exception as e:
            print(f"Error during deployment: {str(e)}")
            return False
    
    def cleanup(self) -> bool:
        """
        Clean up all Kubernetes resources.
        
        Returns:
            bool: True if cleanup was successful
        """
        try:
            # Delete services
            self.v1.delete_namespaced_service(
                name=APP_NAME,
                namespace=NAMESPACE
            )
            self.v1.delete_namespaced_service(
                name="postgres",
                namespace=NAMESPACE
            )
            
            # Delete deployments
            self.apps_v1.delete_namespaced_deployment(
                name=APP_NAME,
                namespace=NAMESPACE
            )
            self.apps_v1.delete_namespaced_deployment(
                name="postgres",
                namespace=NAMESPACE
            )
            
            # Delete PersistentVolumeClaim
            self.v1.delete_namespaced_persistent_volume_claim(
                name="postgres-pvc",
                namespace=NAMESPACE
            )
            
            # Delete ConfigMap
            self.v1.delete_namespaced_config_map(
                name=f"{APP_NAME}-config",
                namespace=NAMESPACE
            )
            
            # Delete namespace
            self.v1.delete_namespace(NAMESPACE)
            
            print("All resources cleaned up successfully")
            return True
        except ApiException as e:
            print(f"Error during cleanup: {str(e)}")
            return False

def main():
    """Main function to deploy or clean up resources."""
    manager = K8sManager()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Manage Kubernetes deployment for FinancialMediator"
    )
    parser.add_argument(
        'action',
        choices=['deploy', 'cleanup'],
        help='Action to perform: deploy or cleanup'
    )
    args = parser.parse_args()
    
    # Perform the requested action
    if args.action == 'deploy':
        success = manager.deploy()
    else:
        success = manager.cleanup()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
