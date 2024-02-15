import sys
from pathlib import Path
src_dir = Path(__file__).resolve()
while src_dir.name != 'src':
    src_dir = src_dir.parent
sys.path.append(str(src_dir))

import json
import inspect
from llm.tooling import generate_tool_description
from llm.my_tools.validation import validate_input
from llm.my_tools import plotting

# Define your functions


# def get_average(avg_var: str, plot: bool = True):
#     """
#     Given a variable name, return the average over time and a corresponding plot. Return format is a dictionary with keys 'average' and 'plot', where the value for 'plot' is a placeholder for a plotly figure.

#     Args:
#         avg_var (string): The variable to average.
#         plot (bool): Whether to return a plot.
#     """
#     pass

# Convert common time and date-describing phrases in the query to the given format "YYYY-MM-DD--YYYY-MM-DD" and "HH:MM--HH:MM" respectively. If only a start date is identified format as "YYYY-MM-DD--"; if only an end date is identified, format as "--YYYY-MM-DD". If only a start time is identified format as "HH:MM--"; if only an end time is identified, format as "--HH:MM". If no days are specified, this field should not be included in the JSON.

def single_event_count(
        v: str, 
        p: list[str] = None,
        dr: str = None,
        tr: str = None,
        d: list[str] = None,
        plot: bool = True):
    """
    Given a variable name corresponding to an event and specifying information, return the event count. If plot is True, return a plot of the event count over time. Return format is a dictionary with keys 'count' and 'plot', where the value for 'plot' is a placeholder for a plotly figure. Return format is a dictionary with keys 'count' and 'plot', where the value for 'plot' is a placeholder string for a plotly figure.

    Args:
        v (string): the event variable
        p (list of strings): people associated with the event
        dr (string): date range of the event
        tr (string): time range of the event
        d (list of strings): days associated with the event
        plot (bool): Whether to return a plot.
    """

    events = validate_input(v, p, dr, tr, d)
    ct = len(events)
    
    plot = plotting.plot_single_event_count(events)

    return {"count": ct, "plot": plot}



# generate_tool_description here


def format_tools():
    current_module = inspect.getmodule(inspect.currentframe())

    def is_function_member(member):
        return (
            inspect.isfunction(member) and member.__module__ == current_module.__name__
        )

    functions = inspect.getmembers(current_module, is_function_member)

    # descriptions = {}
    descriptions = []
    for name, func in functions:
        if name != "format_tools":  # Exclude the description generator function
            # descriptions[name] = generate_tool_description(func)
            descriptions.append(generate_tool_description(func))

    return descriptions


tools = format_tools()
# save this list of dicts to a json
# use the path of this specific file to save the json
tools_jsonpath = Path(__file__).parent / "tools.json"
json.dump(tools, open(tools_jsonpath, "w"), indent=4)