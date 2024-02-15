import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

import json
from datetime import datetime
from pathlib import Path

from server import connect_to_collection

profiles_dir = "/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/Cerebra/data/sim/profiles"


def upsert_data(data, section, profile="llm_v1"):
    """
    Replaces the data in the section with the new data.
    Creates the section if it doesn't exist.
    """
    collection = connect_to_collection()

    # Preparing the document to be inserted
    document = {
        "_id": profile,
        section: data,
    }

    # Use update_one with upsert=True to either update the existing document or insert a new one
    result = collection.update_one(
        {"_id": document["_id"]}, {"$set": document}, upsert=True
    )

    # Check the result
    if result.matched_count > 0 or result.upserted_id:
        print("Document updated or inserted successfully.")
    else:
        print("Failed to update or insert the document.")
        # Inserting the document in MongoDB
        collection.insert_one(document)

        print("Done inserting profile data")


def update_profile_data(
    profile="llm_v1",
):  # , name="Len Matthews"):
    """
    Adds profile data and replaces it if it exists.
    """

    def convert_datetime(x):
        # return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")
        # return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")
        return datetime.strptime(x, "%Y-%m-%dT%H:%M")

    print("Updating profile data")

    final_outputs_dir = Path(profiles_dir) / "llm_v1/outputs/final"
    filepath = final_outputs_dir / "events_breakout.json"

    with open(filepath, "r") as f:
        data = json.load(f)

    for event in data:
        event["start_datetime"] = convert_datetime(event["start_datetime"])
        event["end_datetime"] = convert_datetime(event["end_datetime"])

    # upsert_data(data, "data", profile=profile)
    upsert_data(data, "events", profile=profile)


# old; not sure if useful
def add_to_array(value_to_add, section, profile_id="llm_v1"):
    """
    If it can't find the right array, nothing happens
    """
    collection = connect_to_collection()
    collection.update_one(
        {"profile_id": profile_id}, {"$push": {section: value_to_add}}
    )


def add_entry(key, value, section, profile_id="llm_v1"):
    """ """
    collection = connect_to_collection()
    collection.update_one({"profile_id": profile_id}, {"$set": {section: {key: value}}})
