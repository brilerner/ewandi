import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))


from server.connect import connect_to_db

db = connect_to_db()


collections = db.list_collection_names()
print()
print("Collections in database:", collections)

for collection in collections:
    print(f"\nCollection: {collection}")
    collection = db[collection]

    print(f"Number of unique documents in collection: {collection.count_documents({})}")

    data = collection.find_one()
    events = data["events"]
    event_elements = data["elements"]["events"]
    relations_elements = data["elements"]["relations"]

    print(data)
    print(f"\nID: {data['_id']}")
    print(f"Sections: {data.keys()}")

    print(f"# of events: {len(events)}")
    print(f"# of event elements: {len(event_elements)}")
    print(f"# of relations_elements: {len(relations_elements)}")

    print()
    # print("Sample documents:")
    # sample_data = collection.find().limit(5)
    # for doc in sample_data:
    #     print(doc)

    # print()
    # print("Unique data categories:")
    # unique_values = db.your_collection_name.distinct("data_category")
    # print(unique_values)

# indexes = db.your_collection_name.index_information()
# print(indexes)


### GENERAL

# for collection in collections:
#     print()
#     # print(collection)
#     collection = db[collection]

#     print()
#     print("Number of documents in collection:")
#     print(collection.count_documents({}))

#     print()
#     print("Sample documents:")
#     sample_data = collection.find().limit(5)
#     for doc in sample_data:
#         print(doc)

#     print()
#     print("Unique data categories:")
#     unique_values = db.your_collection_name.distinct("data_category")
#     print(unique_values)
