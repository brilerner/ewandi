import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

import streamlit as st
from pathlib import Path

# from llm import my_tools
from llm.chat import StreamlitSession
from analysis.utils import filter_events, get_all_events, format_datetime
from utils.general import get_root


def set_streamlit_session(debug=False):
    if "session" not in st.session_state:
        st.session_state["session"] = StreamlitSession("brian", debug=debug)
        session = st.session_state["session"]
    else:
        session = st.session_state["session"]
    return session


def convert_event_keys(events, direction="fwd"):
    def convert_event(event):
        # Define a mapping of old keys to new keys

        key_mapping = {
            "start": "start_datetime",
            "end": "end_datetime",
            "title": "name",
        }
        if direction == "rev":
            key_mapping = {v: k for k, v in key_mapping.items()}

        # Create a new dictionary with updated keys
        return {key_mapping.get(key, key): value for key, value in event.items()}

    return [convert_event(event) for event in events]


# set up data path
profile = "llm_v1"
imgs_dir = Path(__file__).resolve().parent / "imgs"
events_dir = (
    get_root() / "data" / "sim" / "profiles" / profile / "outputs" / "streamlit"
)

# set up calendar
raw_events = get_all_events(reformat_datetime=False)
converted_events = convert_event_keys(raw_events, direction="rev")
calendar_events = filter_events(converted_events, {"category": "activity"})

# set up survey
survey_events = filter_events(raw_events, {"source": "survey"})
survey_events = [event for event in survey_events if "value" in event]


# set up sleep
sleep_events = filter_events(raw_events, {"category": "sleep"})
sleep_events = [format_datetime(e.copy()) for e in sleep_events]
sleep_events
for event in sleep_events:
    event["value"] = (
        event["end_datetime"] - event["start_datetime"]
    ).total_seconds() / 3600

bio_text = "Len L. Mays is a junior student-athlete at Duke University, playing for the basketball team. He is currently in-season, and due to his major in Computer Science, is also taking classes. Outside of the court and classroom, Len enjoys going on hikes, playing videogames, and talking to friends, family, and his girlfriend. He has ambitions of making it to the NBA and is intent on optimizing his performance."
