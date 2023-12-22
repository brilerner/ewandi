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
    s = ''.join(char if char.isalnum() else ' ' for char in s)
    
    # Replace multiple spaces with a single space
    s = ' '.join(s.split())
    
    # Convert to lowercase and replace spaces with underscores
    return s.lower().replace(' ', '_')
