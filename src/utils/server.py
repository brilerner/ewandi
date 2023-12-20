
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure


# Local
HOST = 'localhost'
PORT = 27017
DATABASE_NAME = 'CerebraDB'

# Atlas
PASSWORD = "kYQaeGNL0NyOVnAh"
uri = f"mongodb+srv://brianelerner:{PASSWORD}@cerebra.manrrcm.mongodb.net/?retryWrites=true&w=majority"

def connect_to_db(db_loc = 'atlas'):
    if db_loc == 'atlas':
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            # print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    elif db_loc == 'local':
        client = MongoClient(HOST, PORT, serverSelectionTimeoutMS=5000)  # Connects to the default host and port.
        
        try:
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
            # print("MongoDB is running")
        except ConnectionFailure:
            print("MongoDB server is not running")  
    
    db = client[DATABASE_NAME]
    return db

def connect_to_collection(collection: str = 'profiles'):
    db = connect_to_db()
    return db[collection]

def remove_profile(profile):
    """
    Remove a profile from the database.
    """
    collection = connect_to_collection()
    collection.delete_one({'person_id': profile})



