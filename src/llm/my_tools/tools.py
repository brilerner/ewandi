# CAN I AUTOMATE THIS PROCESS???????

tools = [
    {
        "type": "function",
        "function": {
            "name": "tell_joke",
            "description": "Tell a joke about something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "enum": ["atoms", "janitor"],
                        "type": "string",
                        "description": "The topic to make a joke about.",
                    },
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_average",
            "description": "Given a variable name, return the average over time and a corresponding plot. Return format is a dictionary with keys 'average' and 'plot', where the value for 'plot' is a placeholder for a plotly figure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "avg_var": {
                        "enum": ["sleep"],
                        "type": "string",
                        "description": "The variable to average.",
                    },
                },
                "required": ["avg_var"],
            },
        },
    },
]


def tell_joke(topic):
    if topic == "atoms":
        return "Why don't scientists trust atoms? Because they make up everything!"
    elif topic == "janitor":
        return "What did the janitor say when he jumped out of the closet? Supplies!"
    
def get_average(user_id, avg_var):
    from utils.viz import get_plotly_figure, save_temp_plot
    import random
    avg = random.choice([7,8,9])
    fig = get_plotly_figure()
    placeholder = save_temp_plot(fig, user_id)
    return {"average": avg, "placeholder": placeholder}
