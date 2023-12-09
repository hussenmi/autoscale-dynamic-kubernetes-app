import asyncio
import aiohttp
import subprocess

def get_flask_app_url():
    try:
        # Command to get the URL of the Flask app
        result = subprocess.run(["minikube", "service", "flask-app-service", "--url"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return None

async def send_request(session, url):
    async with session.get(url) as response:
        print(f"Response Code: {response.status}")

async def main():
    # Number of concurrent requests
    concurrent_requests = 100

    url = get_flask_app_url()
    if url:
        async with aiohttp.ClientSession() as session:
            tasks = [send_request(session, url) for _ in range(concurrent_requests)]
            await asyncio.gather(*tasks)
    else:
        print("Failed to retrieve the Flask app URL.")

asyncio.run(main())