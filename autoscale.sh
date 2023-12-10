#!/bin/bash

# First, we need to enable the metrics-server addon
echo "Enabling metrics-server addon..."
minikube addons enable metrics-server

# We need to wait for the metrics-server to be fully up and running
echo "Waiting for metrics-server to stabilize..."

sleep 60

# Autoscale Flask app
echo "Autoscaling Flask app..."
kubectl autoscale deployment flask-deployment --min=1 --max=10 --cpu-percent=80

# Simulate load
echo "Starting load simulation on Flask app..."
hey -z 2m -c 700 $(minikube service flask-service --url)


# If we want to use an hpa.yaml file instead of the kubectl autoscale command:
# kubectl apply -f hpa.yaml


# Monitor HPA and Pods
echo "Monitor Horizontal Pod Autoscaler (HPA) using kubeclt get hpa -w"
# kubectl get hpa -w &