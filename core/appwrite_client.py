import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.storage import Storage
load_dotenv()

client = Client()
client.set_endpoint("https://fra.cloud.appwrite.io/v1")  # or your self-hosted URL
client.set_project("6843452b00353fbabc66")
client.set_key("standard_72dbcf2e8350683ffe4d311190e4519e03b737258f33e4fe7c5711b1ea7782234c877ab6b29eba941d891b20e67f0530d472263d94f34f15956437006fc8ea53896c9fb0e3e8fcdccd139750340afe043e07bf4c0a672440e7f13ec561539fcb9069aaf24e8a0e94bd4d1137ff2ed4c5c4689c7b77cbdbf6768967ae19251d96")

storage = Storage(client)
