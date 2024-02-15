import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))
from server.query import get_events
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import logging
def plot_single_event_count(
        events):
    return _occurrence_default(events, type="events")
    

def _occurrence_default(events, type="events"):
    if type == "events":
        key = "event_type_id"
    elif type == "numerical":
        key = "value"

    # Convert the data to a DataFrame
    df = pd.DataFrame(events)
    logging.info(str(df.columns ))
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

    return fig
