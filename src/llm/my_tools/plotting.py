import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src":
    src_dir = src_dir.parent
sys.path.append(str(src_dir))
from server.query import get_events
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import logging


def plot_single_event_count(events):
    return _occurrence_default(events, type="events")


def plot_multiple_event_count(events):
    return _occurrence_default(events, type="events")


def plot_multiple_values(events):
    return _occurrence_default(events, type="numerical")


def _occurrence_default(events, type="events"):
    if type == "events":
        key = "event_type_id"
    elif type == "numerical":
        key = "value"

    # Convert the data to a DataFrame
    df = pd.DataFrame(events)
    logging.info(str(df.columns))
    # Map each event type to a unique integer
    event_type_mapping = {event: i + 1 for i, event in enumerate(df["name"].unique())}
    df["event_type_id"] = df["name"].map(event_type_mapping)

    # Plotting using Plotly
    fig = px.scatter(
        df,
        x="start_datetime",
        y=key,
        color="name",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        # title="Events"
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        legend_title_text="",
        legend=dict(yanchor="middle", y=0.5),
        height=300,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(size=10),  # Adjust font size for smaller labels if necessary
        # xaxis=dict(
            # title_standoff=10  # Reduces the space between the x-axis title and the axis itself
        # ),
    )
    if type == "events":
        fig.update_layout(
            yaxis_title="Event Type",
            yaxis=dict(
                tickmode="array",
                tickvals=list(event_type_mapping.values()),
                ticktext=list(event_type_mapping.keys()),
            ),
        )
    # make plot width smaller

    return fig
