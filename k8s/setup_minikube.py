"""
Script to set up Minikube for FinancialMediator.
"""

import os
import subprocess
import sys
from typing import Optional

def download_minikube() -> bool:
    """
    Download Minikube executable.
    
    Returns:
        bool: True if download was successful
    """
    try:
        url = "https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe"
        minikube_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minikube.exe")
        
        # Download Minikube
        import requests
        response = requests.get(url)
        if response.status_code == 200:
            with open(minikube_path, 'wb') as f:
                f.write(response.content)
            print("Minikube downloaded successfully")
            return True
        else:
            print(f"Failed to download Minikube: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading Minikube: {str(e)}")
        return False

def start_minikube() -> bool:
    """
    Start Minikube with Docker driver.
    
    Returns:
        bool: True if Minikube started successfully
    """
    try:
        # Get the path to minikube.exe
        minikube_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minikube.exe")
        
        # Start Minikube
        result = subprocess.run(
            [minikube_path, "start", "--driver=docker"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Minikube started successfully")
            return True
        else:
            print(f"Error starting Minikube: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error starting Minikube: {str(e)}")
        return False

def check_minikube_status() -> bool:
    """
    Check Minikube status.
    
    Returns:
        bool: True if Minikube is running
    """
    try:
        minikube_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minikube.exe")
        result = subprocess.run(
            [minikube_path, "status"],
            capture_output=True,
            text=True
        )
        
        if "Running" in result.stdout:
            print("Minikube is running")
            return True
        else:
            print("Minikube is not running")
            return False
    except Exception as e:
        print(f"Error checking Minikube status: {str(e)}")
        return False

def main():
    """Main function to set up Minikube."""
    try:
        # Download Minikube if not already downloaded
        if not os.path.exists("minikube.exe"):
            if not download_minikube():
                return 1
        
        # Start Minikube
        if not start_minikube():
            return 1
        
        # Check status
        if not check_minikube_status():
            return 1
        
        print("\nMinikube setup completed successfully!")
        print("You can now use the manager.py script to deploy your application.")
        return 0
    except Exception as e:
        print(f"Error during Minikube setup: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
