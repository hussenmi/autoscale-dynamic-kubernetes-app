# Autoscale Dynamic Kubernetes App

This project contains the necessary configuration files to deploy and autoscale a dynamic web application on Kubernetes. The application uses Flask and is a ToDo application that enables multiple users. It uses a Postgres database for storage and when deployed on Kubernetes, it has a PersistentVolumeClaim, which allows it to retain data even of the database goes down.

A video explaining the features and how it works can be found [here](https://screenapp.io/app/#/shared/b7749401-9f59-4e57-8b2e-95fecb94eaf8).

## File Descriptions

- `app.py`: This is the main Python application file for the Flask web application. It includes the definition of the database models and how the routes should function.

- `requirements.txt`: This file lists the Python dependencies for the application. These are flask, flask-SQLalchemy, and we also need psycopg2-binary because we're working with a postgres database.

- `Dockerfile`: This file is used to build a Docker image for the application.

- `postgres.yaml`: This file defines the necessary Kubernetes resources for deploying a PostgreSQL database. It includes definitions for a Persistent Volume, a Persistent Volume Claim, a Deployment, and a Service.

- `flask.yaml`: This file defines the necessary Kubernetes resources for deploying a Flask application. It includes definitions for a Deployment, and a Service.

- `flask-hpa.yaml`: This file is used to define the HorizontalPodAutoscale resource that tracks CPU utilization. If we want to use this, we can run it as `kubectl apply -f flask-hpa.yaml`, but we can also just use a single command that is given in the `autoscale.sh` file. This is `kubectl autoscale deployment flask-deployment --min=1 --max=10 --cpu-percent=80`. It autoscales the `flask-deployment` by tracking CPU utilization, and if it's above 80%, then the number of pods will increase. We set the minimum number of pods to be 1 and the maximum number of pods to be 10.

The shell files contain the commands that are used to perform some of the tasks. For example, in the `autoscale.sh` file, we see that we need to enable the `metrics-server` addon from minikube for our autoscaling feature to work. And after it stabilizes, we then can perform the autoscale and increase the load on our application to test the autoscaling capabilities. The command to increase the load is also given the file.

The same goes for the other shell files. In the `setup_postgres_flask.sh`, we have the commands that bring up the deployments and allow us to interact with the application.

I have also included a `cassandra.yaml` file that can be used instead of the postgres database but in Kubernetes, it requires some patience for it to stabilize. But once, it does, we can use it in our application, although some configurations need to be changed.