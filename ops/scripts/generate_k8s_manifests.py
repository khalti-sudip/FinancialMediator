import yaml
import os
from jinja2 import Template

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_manifest(template_path, config, output_path):
    with open(template_path, 'r') as f:
        template = Template(f.read())
    
    manifest = template.render(
        app_name=config['app']['name'],
        namespace=config['app']['namespace'],
        replicas=config['app']['replicas'],
        port=config['app']['port'],
        memory_request=config['resources']['memory']['request'],
        memory_limit=config['resources']['memory']['limit'],
        cpu_request=config['resources']['cpu']['request'],
        cpu_limit=config['resources']['cpu']['limit'],
        image=f"{config['image']['repository']}:{config['image']['tag']}",
        service_type=config['service']['type'],
        target_port=config['service']['target_port']
    )
    
    with open(output_path, 'w') as f:
        f.write(manifest)

def main():
    # Load configuration
    config = load_config('ops/config/deploy-config.yaml')
    
    # Generate deployment manifest
    generate_manifest(
        'ops/templates/k8s-deployment.yaml',
        config,
        'ops/k8s/deployment.yaml'
    )
    
    # Generate service manifest
    generate_manifest(
        'ops/templates/k8s-service.yaml',
        config,
        'ops/k8s/service.yaml'
    )

if __name__ == '__main__':
    main()
