import streamlit as st


# from pymongo import MongoClient
# from utils.server import connect_to_db
import streamlit as st
import plotly.express as px
import time
import random
# db = connect_to_db()
# code fetch_data_from_mongodb

# SimulateData.py
# using shell script to start leads to updates not working
# putting things in a class messes with the chat output (duplicate messages)

import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta


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
    )

    # Displaying the figure
    # fig.show()


def main():
    # df = simulate_data()

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Choose a Tab",
        [
            "Overview",
            "Available Data",
            "EwandiChat",
            "App Interaction",
        ],
    )

    if choice == "Overview":
        show_main_tab()
    if choice == "Available Data":
        show_data_visualization_tab()
    if choice == "EwandiChat":
        show_chatbot_tab()
    elif choice == "App Interaction":
        show_app_interaction_tab()
        # st.write("App Interaction Placeholder")


def show_main_tab():
    import streamlit as st

    col1, col2 = st.columns([0.4, 0.6])

    img_path = "/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/Ewandi/src/app/working_examples/streamlit_splash.png"
    with col1:
        st.image(img_path)

    with col2:
        st.header("Text")


def show_chatbot_tab():
    st.header("Chatbot")


def show_data_visualization_tab():
    st.header("Data Visualization")

    # Assuming you have a function to fetch data from MongoDB
    # data = fetch_data_from_mongodb()
    data = simulate_data()

    # Example Plotly visualization
    # fig = px.line(data, x="date", y="value", title="Daily Journal Metrics")
    # st.plotly_chart(fig)

    mood_fig = px.line(data, x="date", y="mood_score", title="Mood Score Over Time")
    event_fig = px.bar(data, x="date", y="num_events", title="Number of Events Per Day")

    st.plotly_chart(mood_fig)
    st.plotly_chart(event_fig)


def show_app_interaction_tab():
    st.header("App Interaction")
    # Code for App Interaction
    tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])

    with tab1:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

    with tab2:
        st.header("A dog")
        st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

    with tab3:
        st.header("An owl")
        st.image("https://static.streamlit.io/examples/owl.jpg", width=200)


if __name__ == "__main__":
    # demo = Demo()
    # demo.main()
    main()
