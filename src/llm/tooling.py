import inspect
import re


def python_type_to_json_type(python_type):
    """
    Converts a Python type to its JSON equivalent as a string.

    Args:
        python_type (type): The Python type to convert.

    Returns:
        str: The JSON type as a string.
    """
    type_mapping = {
        int: "number",
        float: "number",
        str: "string",
        bool: "boolean",
        dict: "object",
        list: "array",
    }

    return type_mapping.get(python_type, "unknown")


def python_value_to_json_value(value):
    if isinstance(value, bool):
        return str(value).lower()
    elif value is None:
        return "null"
    elif isinstance(value, (int, float)):
        if value == float("inf"):
            return "Infinity"
        elif value == float("-inf"):
            return "-Infinity"
        elif value != value:  # check for NaN
            return "NaN"
        return value
    # Add more conversions as needed
    return value

def generate_tool_description(func):
    """
    Generates a dictionary description of a tool function in a specific format.

    Args:
        func (function): The tool function to describe.

    Returns:
        dict: A dictionary containing the tool's description.
    """
    if not callable(func):
        raise ValueError("Provided argument is not a function")

    # Get the docstring
    docstring = inspect.getdoc(func)

    # Extract the main description
    main_description = docstring.split("\n\n")[0]

    # Get the signature
    signature = inspect.signature(func)

    # Build the dictionary
    tool_description = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": main_description,
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    # Extract argument details
    for name, param in signature.parameters.items():
        # get the JSON type
        json_type = python_type_to_json_type(param.annotation)

        # Check if the parameter is required
        is_required = param.default is inspect.Parameter.empty

        # Extract the parameter description from the docstring
        # nor currently using param_type
        param_description = re.search(rf"{name} \((.+?)\): (.+)", docstring)
        if param_description:
            param_type, param_desc = param_description.groups()
        else:
            param_type, param_desc = "No type specified", "No description available"

        # If the parameter has a default value, include it in the description
        if not is_required:
            default_value = python_value_to_json_value(param.default)
            # default_value = param.default
            param_desc += f" (default: {default_value})"

        # Add parameter information to the dictionary
        # tool_description["function"]["parameters"]["properties"][name] = {
        #     "type": param_type,
        #     "description": param_desc,
        # }

        tool_description["function"]["parameters"]["properties"][name] = {
            "type": json_type,
            "description": param_desc,
        }

        if is_required:
            tool_description["function"]["parameters"]["required"].append(name)

    return tool_description
