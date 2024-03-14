from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure


import os

# these dont seem nec
# from dotenv import load_dotenv
# load_dotenv()
# Local
HOST = "localhost"
PORT = 27017
DATABASE_NAME = "EwandiDB"
TIMEOUT_MS = 500

# try:
uri = os.environ["MONGO_URI"]

print(uri)
# client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=TIMEOUT_MS)

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     # print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
