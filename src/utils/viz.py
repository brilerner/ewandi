import numpy as np
from termcolor import colored

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

