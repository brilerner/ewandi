import inspect


def generate_tool_description(func):
    """
    Generates a dictionary description of a tool function.

    Args:
        func (function): The tool function to describe.

    Returns:
        dict: A dictionary containing the tool's description.
    """
    if not callable(func):
        raise ValueError("Provided argument is not a function")

    # Get the docstring
    docstring = inspect.getdoc(func)
    
    # Get the signature
    signature = inspect.signature(func)

    # Build the dictionary
    tool_description = {
        "type": "function"
        "function": {
            "name": func.__name__,
            "description": docstring,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        },
    }

        # Get the JSON type

        # ... existing code ...



    # Extract argument details
    for name, param in signature.parameters.items():

        json_type = python_type_to_json_type(param.annotation)

        tool_description["arguments"][name] = {
            "default": param.default if param.default is not inspect.Parameter.empty else None,
            "type": str(param.annotation) if param.annotation is not inspect.Parameter.empty else "No type specified"
        }

    return tool_description

# Example usage
def example_tool(arg1: int, arg2: str = "default"):
    """
    An example tool function.

    Args:
        arg1 (int): The first argument.
        arg2 (str): The second argument with a default value.
    """
    pass

# Generate the description
description = generate_tool_description(example_tool)
print(description)
