import sys
from pathlib import Path
root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)
from server.query import get_events
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

def plot_occurrence(variable_name,):
    events = get_events(event_name=variable_name)
    plot_events(events)

def plot_events(events, show=False):

    # Convert the data to a DataFrame
    df = pd.DataFrame(events)

    # Map each event type to a unique integer
    event_type_mapping = {event: i+1 for i, event in enumerate(df['name'].unique())}
    df['event_type_id'] = df['name'].map(event_type_mapping)

    # Plotting using Plotly
    fig = px.scatter(df, x='start_datetime', y='event_type_id', color='name', title='Event Schedule')
    fig.update_layout(xaxis_title='Date', yaxis_title='Event Type', yaxis=dict(tickmode='array', tickvals=list(event_type_mapping.values()), ticktext=list(event_type_mapping.keys())))
    if show:
        fig.show()
    else:
        return fig

# plot_occurrence('Basketball Game')