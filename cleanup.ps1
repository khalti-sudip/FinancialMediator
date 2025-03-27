# Delete all resources
kubectl delete -f k8s/deployment.yaml -n financialmediator
kubectl delete -f k8s/service.yaml -n financialmediator
kubectl delete -f k8s/postgres-deployment.yaml -n financialmediator
kubectl delete -f k8s/postgres-service.yaml -n financialmediator
kubectl delete -f k8s/postgres-pv.yaml -n financialmediator
kubectl delete -f k8s/postgres-pvc.yaml -n financialmediator
kubectl delete -f k8s/configmap.yaml -n financialmediator
kubectl delete -f k8s/namespace.yaml

# Stop Minikube
minikube stop
