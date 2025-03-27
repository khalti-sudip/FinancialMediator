#!/bin/bash

# Start Minikube
minikube start --memory=4096 --cpus=2

# Create namespace
kubectl create namespace financial-mediator

# Deploy PostgreSQL
kubectl apply -f ops/k8s/postgres-deployment.yaml -n financial-mediator

# Deploy Redis
kubectl apply -f ops/k8s/redis-deployment.yaml -n financial-mediator

# Deploy OpenTelemetry Collector
kubectl apply -f ops/k8s/otel-collector.yaml -n financial-mediator

# Build and push Docker image
docker build -t docker-desktop:5000/financial-mediator:latest -f ops/docker/Dockerfile .

# Deploy Django application
kubectl apply -f ops/k8s/django-deployment.yaml -n financial-mediator

# Deploy Celery worker
kubectl apply -f ops/k8s/celery-deployment.yaml -n financial-mediator

# Expose the service
kubectl expose deployment financialmediator --type=LoadBalancer --port=80 --target-port=8000 -n financial-mediator

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=financialmediator --timeout=300s -n financial-mediator

# Get service URL
minikube service financialmediator --namespace=financial-mediator --url
