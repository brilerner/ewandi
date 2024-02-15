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

profile = "llm_v1"

setup = True

if setup:
    remove_profile(profile)
    update_profile_data(profile=profile)
    update_eids(profile=profile)
    # data = get_data(profile=profile)

# delete_field("embeddings", profile=profile)
# update_embeddings(profile=profile)

# import time

# start = time.time()
# element_type = "events"
# keystring = "basketball game (activity)"
# nearest_embedding_listings = find_nearest(
#     keystring, threshold=0.11, element_type=element_type, profile=profile
# )
# # print("After find_nearest:", time.time() - start, "seconds")

# elements = get_elements(profile=profile)[element_type]
# nearest_elements = [
#     elements[el["partition"]][el["eid"]] for el in nearest_embedding_listings
# ]
# print([element["name"] for element in nearest_elements])
# end = time.time()
# print(end - start, "seconds")
