import random

import numpy as np


def select_random_members_as_dict(input_dict, num_members=10):
    if len(input_dict) < num_members:
        return "Not enough members in the dictionary to select from."
    selected_items = random.sample(list(input_dict.items()), num_members)
    return dict(selected_items)


def get_sample(values, probabilities=None):
    return np.random.choice(values, p=probabilities)
