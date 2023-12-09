# FROM python:3.8-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the dependencies file to the working directory
# COPY requirements.txt .

# # Install any needed packages specified in requirements.txt
# RUN apt-get update && apt-get install -y libpq-dev
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the content of the local src directory to the working directory
# COPY . .

# # Specify the command to run on container start
# CMD [ "python", "./app.py" ]

# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libpq-dev
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "app.py"]