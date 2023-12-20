import numpy as np

def get_plotly_figure():
    import plotly.graph_objects as go

    # Simulating some data using numpy
    np.random.seed(0)
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(scale=0.2, size=x.shape)

    # Creating a plotly figure
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers+lines', name='Sin with Noise'))
    fig.update_layout(title='Simulated Data: Sine Wave with Noise',
                    xaxis_title='X Axis',
                    yaxis_title='Y Axis')
    return fig


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

# not currently used
def simulate_data():
    random.seed(0)
    start_date = datetime.now() - timedelta(days=120)  # start 4 months ago
    dates = [start_date + timedelta(days=x) for x in range(120)]
    mood_scores = [random.randint(1, 10) for _ in range(120)]
    num_events = [random.randint(0, 5) for _ in range(120)]

    data = pd.DataFrame({
        "date": dates,
        "mood_score": mood_scores,
        "num_events": num_events
    })

    return data

