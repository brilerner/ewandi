def get_value(data, key):
    # Check if data is a dictionary
    if isinstance(data, dict):
        return data.get(key, None)
    # Check if data is an object and has the attribute
    elif hasattr(data, key):
        return getattr(data, key, None)
    else:
        return None