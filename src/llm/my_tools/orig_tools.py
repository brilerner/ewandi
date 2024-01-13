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



"""
The main tools that I want to use are:
1. data extraction (including plotting)
2. RAG

For the data, I need to extract:
- timing
- label name
- condition?
What operations do I want to admit?
dataset operations (hopefully more elegant approach later):
- average, count
- rel
- plot
"""


def retrieve_events(name, conditions=None):

    events = get_events(name, conditions=None)
    return events

def retrieve_entries(query):
    return None


tools_final = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_events",
            "description": "Determine the event name and the associated date and time range if specified so that the events can be retrieved from the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the event.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the event. Format: YYYY-MM-DD",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the event. Format: YYYY-MM-DD",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "The start time of the event. Format: HH:MM:SS",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "The end time of the event. Format: HH:MM:SS",
                    },
                },
                "required": ["name"],
            },
        }
    },
    # {
    #     "type": "function",
    #     "name": "retrieve_entries",
    #     "description": "...",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             "query": {
    #                 "type": "string",
    #                 "description": "The query.",
    #             },
    #         "required": ["query"],
    #         },
    #     }
    # }

]
