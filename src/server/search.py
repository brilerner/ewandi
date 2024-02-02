"""
Retrieving similar embeddings
"""

import numpy as np

from llm.embeddings import request_embedding, get_distance
from server.retrieve import get_embeddings


def get_distances(
    keystring_embedding, db_embeddings, model="text-embedding-3-small", profile="llm_v1"
):
    """
    Find distance from keystring to each element in db_embeddings
    Vectorize for efficiency
    """

    # get embeddings
    embeddings = [embedding["embedding"] for embedding in db_embeddings]

    # get distances
    distances = np.array(
        [get_distance(keystring_embedding, embedding) for embedding in embeddings]
    )
    return distances
    # # sort distances
    # sorted_distances = np.argsort(distances)

    # # get sorted distances
    # sorted_distances = distances[sorted_distances]

    # # get sorted elements
    # sorted_elements = [db_embeddings[i] for i in sorted_distances]

    # return sorted_elements


def find_nearest(
    keystring,
    threshold=0.11,
    element_type="events",
    model="text-embedding-3-small",
    profile="llm_v1",
):
    """
    Find nearest elements to keystring
    """

    db_embeddings = get_embeddings(model=model, profile=profile)[element_type]

    # import time

    # start = time.time()
    # get keystring embedding
    keystring_embedding = request_embedding(keystring, model=model)
    # print("Embedding t:", time.time() - start)

    # start = time.time()
    distances = get_distances(
        keystring_embedding, db_embeddings, model=model, profile=profile
    )
    # print("Distances t:", time.time() - start)

    # print(np.min(distances), np.max(distances))

    # apply threshold and get the indices of the elements that pass
    indices = np.where(distances <= threshold)[0]

    # get the elements that pass
    passed = [db_embeddings[i] for i in indices]

    return passed
