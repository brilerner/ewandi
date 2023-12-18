# from pymongo import MongoClient
# from utils.server import connect_to_db
import streamlit as st
import plotly.express as px


# db = connect_to_db()
# code fetch_data_from_mongodb

# SimulateData.py

import pandas as pd
import random
from datetime import datetime, timedelta

def simulate_data():
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


def main():
    # df = simulate_data()

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Choose a Tab", ["Data Visualization", "App Interaction"])

    if choice == "Data Visualization":
        show_data_visualization_tab()
    elif choice == "App Interaction":
        show_app_interaction_tab()
        # st.write("App Interaction Placeholder")



def show_data_visualization_tab():
    st.header("Data Visualization")
    
    # Assuming you have a function to fetch data from MongoDB
    # data = fetch_data_from_mongodb()
    data = simulate_data()

    # Example Plotly visualization
    # fig = px.line(data, x="date", y="value", title="Daily Journal Metrics")
    # st.plotly_chart(fig)

    mood_fig = px.line(data, x='date', y='mood_score', title='Mood Score Over Time')
    event_fig = px.bar(data, x='date', y='num_events', title='Number of Events Per Day')

    st.plotly_chart(mood_fig)
    st.plotly_chart(event_fig)


def show_app_interaction_tab():
    st.header("App Interaction")
    # Code for App Interaction

if __name__ == "__main__":
    main()
