from locust import HttpUser, between, task

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)  # Simulated users will wait between 1 and 2 seconds between tasks

    @task
    def load_flask_app(self):
        self.client.get("/")  # Assuming your Flask app's main page is the root URL