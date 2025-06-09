import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.storage import Storage
load_dotenv()

project_endpoint = os.getenv("APPWRITE_API_ENDPOINT")
project_id = os.getenv("APPWRITE_PROJECT_ID")
bucket_id = os.getenv("APPWRITE_BUCKET_ID")
api_key = os.getenv("APPWRITE_API_KEY")

client = Client()
client.set_endpoint(project_endpoint)
client.set_project(project_id)
client.set_key(api_key)

storage = Storage(client)
