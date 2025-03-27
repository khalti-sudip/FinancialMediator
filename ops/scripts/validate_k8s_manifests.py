import yaml
from pathlib import Path
import sys

def validate_manifest(manifest_path):
    try:
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
            
        # Validate required fields
        required_fields = [
            'apiVersion',
            'kind',
            'metadata',
            'spec'
        ]
        
        for field in required_fields:
            if field not in manifest:
                print(f"Error: Missing required field '{field}' in {manifest_path}")
                return False
                
        # Validate metadata fields
        metadata_fields = ['name', 'namespace']
        for field in metadata_fields:
            if field not in manifest['metadata']:
                print(f"Error: Missing required metadata field '{field}' in {manifest_path}")
                return False
                
        return True
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {manifest_path}: {e}")
        return False
    except Exception as e:
        print(f"Error validating {manifest_path}: {e}")
        return False

def main():
    k8s_dir = Path('ops/k8s')
    manifest_files = list(k8s_dir.glob('*.yaml'))
    
    if not manifest_files:
        print("No Kubernetes manifest files found in ops/k8s directory")
        sys.exit(1)
    
    for manifest in manifest_files:
        if not validate_manifest(manifest):
            sys.exit(1)
    
    print("All Kubernetes manifests are valid!")

if __name__ == '__main__':
    main()
