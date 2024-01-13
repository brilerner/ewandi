import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)
from server.query import get_events
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px


def plot_occurrence(
    variable_name,
):
    events = get_events(event_name=variable_name)
    plot_events(events)


def _plot(events, type, show):
    if type == "events":
        key = "event_type_id"
    elif type == "numerical":
        key = "value"

    # Convert the data to a DataFrame
    df = pd.DataFrame(events)

    # Map each event type to a unique integer
    event_type_mapping = {event: i + 1 for i, event in enumerate(df["name"].unique())}
    df["event_type_id"] = df["name"].map(event_type_mapping)

    # Plotting using Plotly
    fig = px.scatter(
        df, x="start_datetime", y=key, color="name", title="Event Schedule"
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Event Type",
        yaxis=dict(
            tickmode="array",
            tickvals=list(event_type_mapping.values()),
            ticktext=list(event_type_mapping.keys()),
        ),
    )
    if show:
        fig.show()
    else:
        return fig


def plot_events(events, show=False):
    # Convert the data to a DataFrame
    df = pd.DataFrame(events)

    # Map each event type to a unique integer
    event_type_mapping = {event: i + 1 for i, event in enumerate(df["name"].unique())}
    df["event_type_id"] = df["name"].map(event_type_mapping)

    # Plotting using Plotly
    fig = px.scatter(
        df, x="start_datetime", y="event_type_id", color="name", title="Event Schedule"
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Event Type",
        yaxis=dict(
            tickmode="array",
            tickvals=list(event_type_mapping.values()),
            ticktext=list(event_type_mapping.keys()),
        ),
    )
    if show:
        fig.show()
    else:
        return fig


def plot_numerical(events, show=False):
    import plotly.graph_objects as go

    # Convert to DataFrame
    df = pd.DataFrame(events)

    # Convert start_datetime to datetime object
    df["start_datetime"] = pd.to_datetime(df["start_datetime"])

    # Creating the plot
    fig = go.Figure()

    # Adding a line for each unique event
    for name in df["name"].unique():
        event_df = df[df["name"] == name]
        fig.add_trace(
            go.Scatter(
                x=event_df["start_datetime"],
                y=event_df["value"],
                mode="lines",
                name=name,
            )
        )

    # Updating layout
    fig.update_layout(
        xaxis_title="Date", yaxis_title="Mood", legend_title="Event Names"
    )

    # First, we calculate the average value for each event name
    # average_values = df.groupby('name')['value'].mean().reset_index()

    # # Adding the average line for each unique event
    # for name in average_values['name']:
    #     avg_value = average_values[average_values['name'] == name]['value'].iloc[0]
    #     fig.add_trace(go.Scatter(x=df['start_datetime'].unique(), y=[avg_value] * len(df['start_datetime'].unique()),
    #                             mode='lines', name=f"{name} Average", line=dict(dash='dash')))

    # Show the updated plot
    return fig
    # Show the plot


# plot_occurrence('Basketball Game')
