from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ConfigurationError
import os

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Local
HOST = "localhost"
PORT = 27017
DATABASE_NAME = "CerebraDB"
TIMEOUT_MS = 500

# Atlas
uri = os.environ["MONGO_URI"]

# uri = "rrr"


def connect_to_db(db_loc="atlas"):
    if db_loc == "atlas":

        try:
            # Create a new client and connect to the server
            client = MongoClient(
                uri, 
                server_api=ServerApi("1"), 
                serverSelectionTimeoutMS=TIMEOUT_MS
            )

            client.admin.command("ping")
            # print("Pinged your deployment. You successfully connected to MongoDB!")
        except ConfigurationError as e:
            # this occurs when there is no internet
            print(e)
        except ConnectionFailure as e:
            # this occurs when the connection is not otherwise working
            print(e)

   

    db = client[DATABASE_NAME]
    return db


def connect_to_collection(collection: str = "profiles"):
    db = connect_to_db()
    return db[collection]

if __name__ == "__main__":
    connect_to_db()
    connect_to_collection()
    print("connect.py executed")