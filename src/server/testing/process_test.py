import sys
from pathlib import Path

root_path = "/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src"
sys.path.append(root_path)

from server.search import find_nearest
from server import connect_to_collection
from server.remove import delete_field, remove_profile
from server.retrieve import get_data, get_elements
from server.routines import update_eids, update_embeddings
from server.transfer import upsert_data, update_profile_data

# profile = "test"
profile = "test"

events = [
    {
        "name": "basketball game",
        "start_datetime": "2023-09-01T10:00",
        "end_datetime": "2023-09-01T11:00",
        "description": "Event 1 description.",
        "category": "activity",
        "people": [
            {
                "name": "P1",
                "description": "Friend from home who goes to the same college.",
                "category": "person",
            },
        ],
    },
    {
        "name": "cooking",
        "start_datetime": "2023-09-01T10:00",
        "end_datetime": "2023-09-01T11:00",
        "description": "Event 2 description.",
        "category": "activity",
        "people": [
            # {
            #     "name": "P2",
            #     "description": "Friend from home who goes to the same college.",
            #     "category": "person",
            # },
            {
                "name": "P1",
                "description": "Friend from home who goes to the same college.",
                "category": "person",
            },
        ],
    },
]

setup = False

if setup:
    remove_profile(profile)
    upsert_data(events, "events", profile=profile)
    update_eids(profile=profile)
    # data = get_data(profile=profile)

# delete_field("embeddings", profile=profile)
# update_embeddings(profile=profile)

# import time

# start = time.time()
element_type = "events"
keystring = "basketball game (activity)"
nearest_embedding_listings = find_nearest(
    keystring, threshold=0.11, element_type=element_type, profile=profile
)
# print("After find_nearest:", time.time() - start, "seconds")

elements = get_elements(profile=profile)[element_type]
nearest_elements = [
    elements[el["partition"]][el["eid"]] for el in nearest_embedding_listings
]
# print([element["name"] for element in nearest_elements])
# end = time.time()
# print(end - start, "seconds")
