from utils.server import connect_to_db

db = connect_to_db()
print(db.list_collection_names())