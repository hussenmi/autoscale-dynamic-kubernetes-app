#!/bin/bash

# Simulate load
echo "Starting load simulation on Flask app..."
# ab -n 100000 -c 8000 http://$(minikube service flask-app-service --url)/
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.005; do wget -q -O- http://$(minikube ip):30007; done"

# Monitor HPA and Pods
echo "Monitoring Horizontal Pod Autoscaler (HPA)..."
# kubectl get hpa -w &

# echo "Monitoring pods..."
# kubectl get pods -w