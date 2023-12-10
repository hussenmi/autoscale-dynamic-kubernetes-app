#!/bin/bash

# Tearing down Flask app and Cassandra
echo "Tearing down Flask app and Postgres..."
kubectl delete -f flask.yaml
kubectl delete -f postgres.yaml