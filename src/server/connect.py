from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
import os

from dotenv import load_dotenv
from pymongo.errors import ConfigurationError

# Load environment variables from .env file
load_dotenv()

# Local
HOST = "localhost"
PORT = 27017
# DATABASE_NAME = "EwandiDB"
DATABASE_NAME = "CerebraDB"
TIMEOUT_MS = 500

# Atlas
uri = os.environ["MONGO_URI"]


def connect_to_db(db_loc="atlas"):
    if db_loc == "atlas":
        # Create a new client and connect to the server
        try:
            client = MongoClient(
                uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=TIMEOUT_MS
            )
        except ConfigurationError as e:
            # this occurs when there is no internet
            print(e)
            raise ConfigurationError

        # Send a ping to confirm a successful connection
        try:
            client.admin.command("ping")
            # print("Pinged your deployment. You successfully connected to MongoDB!")
        except ConnectionFailure as e:
            # this occurs when the connection is not otherwise working
            print(e)
            raise ConnectionFailure

    elif db_loc == "local":
        client = MongoClient(
            HOST, PORT, serverSelectionTimeoutMS=TIMEOUT_MS
        )  # Connects to the default host and port.

        try:
            # The ismaster command is cheap and does not require auth.
            client.admin.command("ismaster")
            # print("MongoDB is running")
        except ConnectionFailure:
            print("MongoDB server is not running")

    db = client[DATABASE_NAME]
    return db


def connect_to_collection(collection: str = "profiles"):
    db = connect_to_db()
    return db[collection]
