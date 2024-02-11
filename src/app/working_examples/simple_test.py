import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

import streamlit as st

st.set_page_config(layout="wide", page_title="Cerebra Demo")
import plotly.express as px
from streamlit_calendar import calendar
import numpy as np
from pathlib import Path
from utils.test import test_streamlit


imgs_dir = Path(__file__).resolve().parent / "imgs"

calendar_options = {
    "editable": "true",
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridDay,dayGridWeek,dayGridMonth",
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "18:00:00",
    "initialView": "dayGridMonth",
    "resourceGroupField": "building",
    "resources": [
        {"id": "a", "building": "Building Ae", "title": "Building Ae"},
        {"id": "b", "building": "Building A", "title": "Building B"},
        {"id": "c", "building": "Building B", "title": "Building C"},
        {"id": "d", "building": "Building B", "title": "Building D"},
        {"id": "e", "building": "Building C", "title": "Building E"},
        {"id": "f", "building": "Building C", "title": "Building F"},
    ],
}
calendar_events = [
    {
        "title": "Event 2",
        "start": "2024-01-01T08:30:00",
        "end": "2024-01-01T10:30:00",
        "resourceId": "a",
        "location": "K Center",
    },
    {
        "title": "Event 1",
        "start": "2024-01-01T07:30:00",
        "end": "2024-01-01T10:30:00",
        "resourceId": "b",
    },
    {
        "title": "Event 3",
        "start": "2024-01-01T10:40:00",
        "end": "2024-01-01T12:30:00",
        "resourceId": "a",
    },
]
custom_css = """
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 1rem;
    }
"""


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
    return fig


def format_event_data(event_data):
    formatted_data = f"**Event Title:** {event_data.get('title')}\n\n"
    formatted_data += f"**Start Time:** {event_data.get('start')}\n"
    formatted_data += f"**End Time:** {event_data.get('end')}\n"
    return formatted_data


def parse_callback(calendar_component):
    if calendar_component.get("callback", "") == "eventClick":
        cb = calendar_component.get("eventClick")
        event = cb["event"]
        st.markdown(format_event_data(event))


def show_calendar_with_output():
    col1, col2 = st.columns([2, 1])

    with col1:
        # Create the calendar with the callback
        calendar_component = calendar(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            # callbacks="eventClick",  # Add callback function
        )

    with col2:
        st.header("Event Details")
        parse_callback(calendar_component)


def main():
    choice = st.sidebar.radio(
        "Choose a Tab",
        [
            "Introduction",
            "Bio",
            "Explore",
            "Chat",
        ],
    )

    if choice == "Introduction":
        show_overview_tab()
    if choice == "Bio":
        show_bio_tab()
    if choice == "Explore":
        show_dataset_tab()
    if choice == "Chat":
        show_chatbot_tab()


def show_overview_tab():
    st.header("Overview")
    st.write("Welcome to Cerebra...")


def show_bio_tab():
    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        img_path = imgs_dir / "llm.png"
        st.image(str(img_path))

    with col2:
        st.header("Len's Bio")
        st.write(
            "Len L. Mays is a junior student-athlete at Duke University, playing for the basketball team. He is currently in-season, and due to his major in Computer Science, is also taking classes. Outside of the court and classroom, Len enjoys going on hikes, playing videogames, and talking to friends, family, and his girlfriend. He has ambitions of making it to the NBA and is intent on optimizing his performance."
        )


def show_dataset_tab():
    st.header("Available Data")

    tab1, tab2, tab3 = st.tabs(["Schedule", "Nutrition", "Survey"])

    with tab1:
        show_calendar_with_output()

    with tab2:
        st.write("Nutrition Placeholder")

    with tab3:
        st.plotly_chart(get_plotly_figure())


def show_chatbot_tab():
    prompt = st.chat_input("Say something")
    if prompt:
        st.write(f"User has sent the following prompt: {prompt}")
        test_streamlit(st.write)


if __name__ == "__main__":
    main()
