#!/bin/bash

# Setting Docker environment to Minikube's Docker daemon
echo "Setting Docker environment to Minikube's Docker daemon..."
eval $(minikube docker-env)

# Building Flask app Docker image with no cache
echo "Building Flask app Docker image..."
docker build -t todo-flask-app .

# Deploying Postgres
echo "Deploying Postgres..."
kubectl apply -f postgres.yaml

# Wait for Postgres to be fully up and running
echo "Waiting for Postgres to stabilize..."
sleep 10

# Deploying Flask app
echo "Deploying Flask app..."
kubectl apply -f flask.yaml

# Wait for the Flask app to stabilize
echo "Waiting for Flask app to stabilize..."
sleep 90

# Getting Flask app service URL
echo "Retrieving Flask app service URL..."
minikube service flask-service --url
echo