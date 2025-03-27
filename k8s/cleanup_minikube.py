"""
Script to clean up Minikube environment.
"""

import os
import subprocess
import sys
from typing import Optional

def stop_minikube() -> bool:
    """
    Stop Minikube.
    
    Returns:
        bool: True if Minikube stopped successfully
    """
    try:
        minikube_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minikube.exe")
        result = subprocess.run(
            [minikube_path, "stop"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Minikube stopped successfully")
            return True
        else:
            print(f"Error stopping Minikube: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error stopping Minikube: {str(e)}")
        return False

def delete_minikube() -> bool:
    """
    Delete Minikube.
    
    Returns:
        bool: True if Minikube deleted successfully
    """
    try:
        minikube_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minikube.exe")
        result = subprocess.run(
            [minikube_path, "delete"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Minikube deleted successfully")
            return True
        else:
            print(f"Error deleting Minikube: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error deleting Minikube: {str(e)}")
        return False

def cleanup_files() -> bool:
    """
    Clean up downloaded files.
    
    Returns:
        bool: True if cleanup was successful
    """
    try:
        minikube_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minikube.exe")
        if os.path.exists(minikube_path):
            os.remove(minikube_path)
            print("Minikube executable removed")
        return True
    except Exception as e:
        print(f"Error cleaning up files: {str(e)}")
        return False

def main():
    """Main function to clean up Minikube environment."""
    try:
        # Stop Minikube
        if not stop_minikube():
            return 1
        
        # Delete Minikube
        if not delete_minikube():
            return 1
        
        # Clean up files
        if not cleanup_files():
            return 1
        
        print("\nMinikube cleanup completed successfully!")
        return 0
    except Exception as e:
        print(f"Error during Minikube cleanup: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
