# Start Minikube
minikube start --driver=docker

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap
kubectl apply -f k8s/configmap.yaml

# Create PostgreSQL resources
kubectl apply -f k8s/postgres-pv.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..."
Start-Sleep -Seconds 30

# Create application resources
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Get the NodePort for the application
$service = kubectl get svc -n financialmediator financialmediator -o json
$nodePort = ($service | ConvertFrom-Json).spec.ports[0].nodePort
$minikubeIp = minikube ip

Write-Host "Application is running at: http://$minikubeIp:$nodePort"
Write-Host "You can access the admin interface at: http://$minikubeIp:$nodePort/admin"
