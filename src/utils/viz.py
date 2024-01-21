import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)
import logging
import numpy as np



def temp_plot_placeholder(delimiter="PPP"):
    """
    Generate a placeholder for a temporary plot.
    The placeholder is "PPP" + 4 random letters that are not P + "PPP".
    """
    import random

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    placeholder = delimiter
    for _ in range(4):
        letter = random.choice(letters)
        while letter == "P":
            letter = random.choice(letters)
        placeholder += letter
    placeholder += delimiter
    return placeholder


def save_temp_plot(fig, user_id):
    """
    Save a plotly figure to a specified directory.
    Do using pickle.
    """
    import pickle

    file_placeholder = temp_plot_placeholder()

    save_dir = Path(root_path) / "tmp" / user_id / "plots"
    save_path = save_dir / (file_placeholder + ".pkl")
    with open(save_path, "wb") as file:
        pickle.dump(fig, file)
    return file_placeholder


def load_temp_plot(session, file_placeholder):
    """
    Load a plotly figure from a specified directory.
    Do using pickle.
    """
    import pickle

    save_dir = Path(root_path) / "tmp" / session.userid / "plots"
    save_path = save_dir / (file_placeholder + ".pkl")
    with open(save_path, "rb") as file:
        fig = pickle.load(file)
    return fig


def show_temp_plot(file_placeholder):
    fig = load_temp_plot(file_placeholder)
    fig.show()


def get_plotly_figure():
    import plotly.graph_objects as go

    # Simulating some data using numpy
    np.random.seed(0)
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(scale=0.2, size=x.shape)

    # Creating a plotly figure
    fig = go.Figure(
        data=go.Scatter(x=x, y=y, mode="markers+lines", name="Sin with Noise")
    )
    fig.update_layout(
        title="Simulated Data: Sine Wave with Noise",
        xaxis_title="X Axis",
        yaxis_title="Y Axis",
        height=300,
    )
    return fig


# not currently used
def simulate_data():
    random.seed(0)
    start_date = datetime.now() - timedelta(days=120)  # start 4 months ago
    dates = [start_date + timedelta(days=x) for x in range(120)]
    mood_scores = [random.randint(1, 10) for _ in range(120)]
    num_events = [random.randint(0, 5) for _ in range(120)]

    data = pd.DataFrame(
        {"date": dates, "mood_score": mood_scores, "num_events": num_events}
    )

    return data
