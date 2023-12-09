#!/bin/bash

# Tearing down Flask app and Cassandra
echo "Tearing down Flask app and Cassandra..."
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
kubectl delete -f cassandra-service.yaml
kubectl delete -f cassandra-deployment.yaml