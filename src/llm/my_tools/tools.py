import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(root_path)

import inspect
from llm.tooling import generate_tool_description

# Define your functions


def get_average(avg_var: str, plot: bool = True):
    """
    Given a variable name, return the average over time and a corresponding plot. Return format is a dictionary with keys 'average' and 'plot', where the value for 'plot' is a placeholder for a plotly figure.

    Args:
        avg_var (string): The variable to average.
        plot (bool): Whether to return a plot.
    """
    pass


# generate_tool_description here


def format_tools():
    current_module = inspect.getmodule(inspect.currentframe())

    def is_function_member(member):
        return (
            inspect.isfunction(member) and member.__module__ == current_module.__name__
        )

    functions = inspect.getmembers(current_module, is_function_member)

    descriptions = {}
    for name, func in functions:
        if name != "format_tools":  # Exclude the description generator function
            descriptions[name] = generate_tool_description(func)

    return descriptions


tools = format_tools()
# x
