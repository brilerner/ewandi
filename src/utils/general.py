def generate_uid():
    import uuid

    return uuid.uuid4()


def get_root():
    from pathlib import Path

    cwd = Path.cwd().resolve()
    while cwd.name != "cerebra":
        cwd = cwd.parent
    return cwd


def get_value(data, key):
    # Check if data is a dictionary
    if isinstance(data, dict):
        return data.get(key, None)
    # Check if data is an object and has the attribute
    elif hasattr(data, key):
        return getattr(data, key, None)
    else:
        return None


def to_snake_case(s):
    """
    Converts a given string into snake_case.

    :param s: String to be converted
    :return: String in snake_case
    """
    # Replace all non-alphanumeric characters with spaces
    s = "".join(char if char.isalnum() else " " for char in s)

    # Replace multiple spaces with a single space
    s = " ".join(s.split())

    # Convert to lowercase and replace spaces with underscores
    return s.lower().replace(" ", "_")


def update_score(current_score, changes=[1, 0, -1], probabilities=None):
    """
    Updates a score based on given changes and probabilities.

    Parameters:
    current_score (int or float): Current score.
    changes (list): List of possible changes (can be int or float). Default is [1, 0, -1].
    probabilities (list): Corresponding probabilities for each change. Default is equal probability for each change.

    Returns:
    int or float: Updated score.
    """
    import math
    import random

    # Set equal probabilities if none provided
    if probabilities is None:
        probabilities = [1 / len(changes)] * len(changes)

    # Ensure the probabilities sum up to 1
    if not math.isclose(sum(probabilities), 1, abs_tol=0.001):
        raise ValueError("Probabilities must sum up to 1")

    # Choose a change based on the given probabilities
    change = random.choices(changes, weights=probabilities, k=1)[0]

    # Update and return the new score
    new_score = current_score + change
    return new_score


# Function to parse days into a standardized format
def enforce_list(_):
    if isinstance(_, list):
        return _
    else:
        return [_]


def lowercase_first_letter(s):
    if not s:
        return s
    return s[0].lower() + s[1:]
