#!/usr/bin/env python3
"""
Kubernetes deployment script for FinancialMediator
"""

import subprocess
import os
import sys
from pathlib import Path

class KubernetesDeployer:
    def __init__(self, k8s_dir: str):
        self.k8s_dir = Path(k8s_dir)
        self.kubectl = "kubectl"

    def configure_k8s(self):
        """Configure Kubernetes context"""
        try:
            subprocess.run([self.kubectl, "config", "set-context", "default"], check=True)
            subprocess.run([self.kubectl, "config", "use-context", "default"], check=True)
            print("Kubernetes context configured successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error configuring Kubernetes: {e}")
            sys.exit(1)

    def apply_manifests(self):
        """Apply all Kubernetes manifests"""
        manifests = [
            "secrets/secrets.yaml",
            "deployments/django-deployment.yaml",
            "services/django-service.yaml",
            "persistence/pvc.yaml",
            "hpa/hpa.yaml"
        ]

        for manifest in manifests:
            manifest_path = self.k8s_dir / manifest
            if manifest_path.exists():
                try:
                    subprocess.run([self.kubectl, "apply", "-f", str(manifest_path)], check=True)
                    print(f"Applied {manifest}")
                except subprocess.CalledProcessError as e:
                    print(f"Error applying {manifest}: {e}")
                    sys.exit(1)
            else:
                print(f"Warning: Manifest {manifest} not found")

    def wait_for_deployment(self):
        """Wait for deployment to be ready"""
        try:
            subprocess.run([self.kubectl, "rollout", "status", "deployment/financialmediator"], check=True)
            subprocess.run([self.kubectl, "get", "pods"], check=True)
            print("Deployment successful")
        except subprocess.CalledProcessError as e:
            print(f"Error waiting for deployment: {e}")
            sys.exit(1)

    def deploy(self):
        """Run the complete deployment process"""
        print("Starting Kubernetes deployment...")
        
        self.configure_k8s()
        self.apply_manifests()
        self.wait_for_deployment()

def main():
    k8s_dir = Path(__file__).parent.parent / "k8s"
    if not k8s_dir.exists():
        print(f"Error: Kubernetes directory {k8s_dir} not found")
        sys.exit(1)

    deployer = KubernetesDeployer(str(k8s_dir))
    deployer.deploy()

if __name__ == "__main__":
    main()
