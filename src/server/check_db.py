from utils.server import connect_to_db

db = connect_to_db()


collections = db.list_collection_names()
print()
print("Collections in database:", collections)

for collection in collections:
    print()
    print(collection)
    collection = db[collection]

    print()
    print("Number of documents in collection:")
    print(collection.count_documents({}))

    print()
    print("Sample documents:")
    sample_data = collection.find().limit(5)
    for doc in sample_data:
        print(doc)

    print()
    print("Unique data categories:")
    unique_values = db.your_collection_name.distinct('data_category')
    print(unique_values)

# indexes = db.your_collection_name.index_information()
# print(indexes)
