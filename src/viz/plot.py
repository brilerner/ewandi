import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')
from server.query_data import get_events
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

def plot_occurrence(variable_name):
    events = get_events(event_name=variable_name)
    plot_events(events)

def plot_events(events):

    # Convert the data to a DataFrame
    data = events[0]['calendar_events']
    df = pd.DataFrame(data)

    # Map each event type to a unique integer
    event_type_mapping = {event: i+1 for i, event in enumerate(df['name'].unique())}
    df['event_type_id'] = df['name'].map(event_type_mapping)

    # Plotting using Plotly
    fig = px.scatter(df, x='start_datetime', y='event_type_id', color='name', title='Event Schedule')
    fig.update_layout(xaxis_title='Date', yaxis_title='Event Type', yaxis=dict(tickmode='array', tickvals=list(event_type_mapping.values()), ticktext=list(event_type_mapping.keys())))
    fig.show()

# plot_occurrence('Basketball Game')