import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

from server import connect_to_db, connect_to_collection


def delete_field(field, profile="llm_v1"):
    collection = connect_to_collection()
    # Use $unset to delete the specified field
    collection.update_one({"_id": profile}, {"$unset": {field: ""}})
    print(f"Removed section: {field}")


def remove_profile(profile="llm_v1"):
    """
    Remove a profile from the database.
    """
    collection = connect_to_collection()
    collection.delete_one({"_id": profile})
    print(f"Removed profile: {profile}")


def delete_collections(collection_name=None):
    db = connect_to_db()

    if collection_name:
        # Delete only the specified collection
        print(f"Dropping collection: {collection_name}")
        db[collection_name].drop()
    else:
        # Delete all collections in the database
        collections = db.list_collection_names()
        for col_name in collections:
            print(f"Dropping collection: {col_name}")
            db[col_name].drop()

    print("Operation completed.")


# if __name__ == 'main': # using this causes RuntimeError: can't create new thread at interpreter shutdown
# delete_collections()


# # Usage examples:

# # Replace 'your_database_name' with the name of your database

# # Delete all collections in the database
# delete_collections('your_database_name')

# # Delete only a specific collection, e.g., 'your_collection_name'
# # delete_collections('your_database_name', 'your_collection_name')


# # Drop an entire collection
# collection.drop()
