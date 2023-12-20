# from pymongo import MongoClient
# from utils.server import connect_to_db
import streamlit as st
import plotly.express as px
import time
import random
from openai import OpenAI
# db = connect_to_db()
# code fetch_data_from_mongodb

# SimulateData.py
# using shell script to start leads to updates not working
#putting things in a class messes with the chat output (duplicate messages)

import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta

client = OpenAI()#api_key=st.secrets["OPENAI_API_KEY"])

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

    # Displaying the figure
    # fig.show()


def main():
    # df = simulate_data()

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Choose a Tab", [
        "Chatbot",
        "Data Visualization", 
        # "App Interaction",
    ])

    if choice == "Chatbot":
        # st.write("Chatbot Placeholder")
        show_chatbot_tab()
    if choice == "Data Visualization":
        show_data_visualization_tab()
    # elif choice == "App Interaction":
    #     show_app_interaction_tab()
    #     # st.write("App Interaction Placeholder")

def show_chatbot_tab():
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

def show_chatbot_tab_old():
    st.header("Chatbot")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            assistant_response = random.choice(
                [
                    "Hello there! How can I assist you today?",
                    "Hi, human! Is there anything I can help you with?",
                    "Do you need help?",
                ]
            )
            # Simulate stream of response with milliseconds delay
            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

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
    # demo = Demo()
    # demo.main()
    main()
