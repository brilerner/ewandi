import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)


import streamlit as st

st.set_page_config(layout="wide", page_title="Cerebra Demo")
from streamlit_calendar import calendar
import numpy as np
from pathlib import Path
import prompts
import app_text
from utils.general import get_root

# from utils.io import load_json
from viz.plot import plot_events
from llm.chat import start_cerebra_session, cerebra_completion_request
from openai import OpenAI
import time
import random
# import logging

profile = "llm_v1"
imgs_dir = Path(__file__).resolve().parent / "imgs"
events_dir = (
    get_root() / "data" / "sim" / "profiles" / profile / "outputs" / "streamlit"
)

openers = prompts.engine.openers
# start session
# st.session_state.session = start_cerebra_session()


#### Dataset Tabs
def load_json(file_path):
    """
    Load a JSON template file and return its content.

    Args:
    file_path (str): Path to the JSON file.

    Returns:
    dict: Content of the JSON file.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def convert_event_keys(events):
    def convert_event(event):
        # Define a mapping of old keys to new keys
        key_mapping = {
            "start": "start_datetime",
            "end": "end_datetime",
            "title": "name",
        }

        # Create a new dictionary with updated keys
        return {key_mapping.get(key, key): value for key, value in event.items()}

    return [convert_event(event) for event in events]


def show_calendar_hub_tab():
    def parse_stcalendar_callback(calendar_component, formatter):
        if calendar_component.get("callback", "") == "eventClick":
            cb = calendar_component.get("eventClick")
            event = cb["event"]
            st.markdown(formatter(event))

    def format_calendar_data(event_data):
        formatted_data = f"**Event Title:** {event_data.get('title')}\n\n"
        formatted_data += f"**Start Time:** {event_data.get('start')}\n"
        formatted_data += f"**End Time:** {event_data.get('end')}\n"
        return formatted_data

    def format_journal_data(event_data):
        return str(event_data)

    def format_nutrition_data(event_data):
        return str(event_data)

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

    calendar_options = {
        "editable": "false",
        "selectable": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridDay,dayGridWeek,dayGridMonth",
        },
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
        "initialView": "dayGridDay",
    }

    # calculate first day and start with that

    color_dict = {"calendar": "#0000ff", "journal": "#ff0000", "nutrition": "#008000"}

    all_events = []
    for k, c in color_dict.items():
        events = load_json(events_dir / f"{k}_events.json")
        for event in events:
            event["category"] = k
            event["backgroundColor"] = c
        all_events.extend(events)

    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.write("Calendar")
        # Create the calendar with the callback
        calendar_component = calendar(
            events=all_events,
            options=calendar_options,
            custom_css=custom_css,
            # key="calendar",
            # callbacks="eventClick",  # Add callback function
        )

    with col2:
        st.header("Event Details")
        parse_stcalendar_callback(calendar_component, format_calendar_data)


def show_sleep_tab():
    def plot_sleep(event_data):
        fig = plot_events(event_data)
        st.plotly_chart(fig)

    events = load_json(events_dir / "sleep_events.json")
    events = convert_event_keys(events)
    plot_sleep(events)


def show_survey_tab():
    def plot_survey(event_data):
        fig = plot_events(event_data)
        st.plotly_chart(fig)

    events = load_json(events_dir / "survey_events.json")
    events = convert_event_keys(events)
    plot_survey(events)


#### main tabs


def show_overview_tab():
    st.header("Overview")

    st.write("Welcome to Cerebra...")
    st.write(app_text.intro)


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

    tabs = [
        "Calendar Hub",
        "Sleep Tracker",
        "End-of-Day Survey",
    ]

    tab1, tab2, tab3 = st.tabs(tabs)

    with tab1:
        show_calendar_hub_tab()

    with tab2:
        show_sleep_tab()

    with tab3:
        show_survey_tab()


def show_chatbot_tab():
    def plot_to_streamlit(plot):
        st.plotly_chart(plot)

    if "messages" not in st.session_state:
        # st.write("Resetting messages")
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = "brian"
    if "client" not in st.session_state:
        st.session_state["client"] = OpenAI()
    if "backoff" not in st.session_state:
        st.session_state["backoff"] = True
    # display non-tool messages
    # for message in st.session_state.session.conversation.get_display_messages():
    for message in st.session_state.messages:
        # if message["role"] != "system" and message["role"] != "tool":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # opener = prompts.engine.get_opener()
    opener = random.choice(openers)
    if prompt := st.chat_input(opener):
        # add user input to conversation
        st.session_state.messages.append({"role": "user", "content": prompt})
        # time.sleep(5)
        # st.session_state.session.conversation.messages.append(
        #     {"role": "user", "content": prompt}
        # )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            # run request
            message = cerebra_completion_request(
                st.session_state,
                # st.session_state.session,
                stream_handler=message_placeholder.markdown,
                plot_handler=plot_to_streamlit,
            )
        st.session_state.messages.append(message)

        # # (response.choices[0].delta.content or "")
        # def stream_to_streamlit(message_chunk):
        #     streamed_message += message_chunk
        #     # logging.info(f"full response: {full_response}")
        #     message_placeholder.markdown(streamed_message + "▌")

    #    with st.chat_message("assistant"):
    #         message_placeholder = st.empty()
    #         response = "This is a test response"
    #         time.sleep(2)
    #         message_placeholder.markdown(response)


def main():
    tabs = [
        "Overview",
        "Learn about Len",
        "Explore the Data",
        "Chat with Cerebra",
    ]

    tab_funcs = [
        show_chatbot_tab,
        show_overview_tab,
        show_bio_tab,
        show_dataset_tab,
    ]

    choice = st.sidebar.radio("Choose a Tab", tabs)

    for i, t in enumerate(tabs):
        if choice == t:
            tab_funcs[i]()
    # if choice == tabs[0]:
    #     show_overview_tab()
    # if choice == tabs[1]:
    #     show_bio_tab()
    # if choice == tabs[2]:
    #     show_dataset_tab()
    # if choice == tabs[3]:
    #     show_chatbot_tab()


if __name__ == "__main__":
    main()

# if "session" not in st.session_state:
# logging.info(st.session_state)

# st.session_state["session"] = start_cerebra_session()


# with st.chat_message("user"):
#     st.write("How many occurrences of Basketball Game are there?")

# Accept user input; uses walrus operator
# if prompt := st.chat_input(PROMPTS.opener):
# if prompt == "q":
#     prompt = "How many occurrences of Basketball Game are there?"
# conversation.messages.append({"role": "user", "content": prompt})

# testing = True
# if testing:
# prompt = "How many occurrences of Basketball Game are there?"
