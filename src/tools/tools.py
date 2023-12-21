import logging
import json
from utils.general import get_value
from server.query import get_n_occurrences

tools = [
{
        "type": "function",
        "function": {
            "name": "get_occurrence",
            "description": "Tell the number of occurrences to the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variable": {
                        "type": "string",
                        "description": "The variable to describe.",
                    },
                },
                "required": ["variable"],
            },
        }
    },
]

def call_function(function, conversation):
    name = function["name"]
    logging.info(f"Function call: {name}")

    if name == "get_occurrence":
        try:
            fargs = json.loads(function["arguments"])
            n = get_n_occurrences(**fargs)
            # fig, n = get_occurrence_information(**function_arguments)
            return n # how to show fig???
        
        except Exception as e:
            logging.exception(f"Function {name} execution failed")
            print(f"Function execution failed")
            print(f"Error message: {e}")
    else:
        logging.exception(f"Function {name} does not exist and cannot be called")
        raise Exception("Function does not exist and cannot be called")

def call_function_v2(name, args):
    logging.info(f"Function call: {name}")

    if name == "get_occurrence":
        try:
            n = get_n_occurrences(**args)
            # fig, n = get_occurrence_information(**function_arguments)
            return n # how to show fig???
        
        except Exception as e:
            logging.exception(f"Function {name} execution failed")
            print(f"Function execution failed")
            print(f"Error message: {e}")
    else:
        logging.exception(f"Function {name} does not exist and cannot be called")
        raise Exception("Function does not exist and cannot be called")

def get_occurrence_information(variable):
    logging.info(f"Running get_occurrence_information for argument: {variable}")
    # fig = plot_occurrence(variable)
    n = get_n_occurrences(variable)
    return n
