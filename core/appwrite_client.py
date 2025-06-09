import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.storage import Storage

# Load .env file
load_dotenv()

# Fetch environment variables safely
project_endpoint = os.getenv("APPWRITE_API_ENDPOINT")
project_id = os.getenv("APPWRITE_PROJECT_ID")
bucket_id = os.getenv("APPWRITE_BUCKET_ID")
api_key = os.getenv("APPWRITE_API_KEY")

# Basic validation (optional but recommended)
if not all([project_endpoint, project_id, bucket_id, api_key]):
    raise ValueError("❌ One or more Appwrite environment variables are missing.")

# Initialize Appwrite client
client = Client()
client.set_endpoint(project_endpoint)
client.set_project(project_id)
client.set_key(api_key)

# Initialize Appwrite storage service
storage = Storage(client)
