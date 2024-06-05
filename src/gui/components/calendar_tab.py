import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

import streamlit as st
from streamlit_calendar import calendar as streamlit_calendar
from gui.streamlit_setup import calendar_events


def show_calendar(color_mapping=None):
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

    # def format_journal_data(event_data):
    #     return str(event_data)

    # def format_nutrition_data(event_data):
    #     return str(event_data)

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
            "left": "prev,next",
            # "left": "today prev,next",
            "center": "title",
            "right": "dayGridDay,dayGridWeek,dayGridMonth",
        },
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
        "initialView": "dayGridMonth",
        "initialDate": "2023-09-01",
    }

    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.write("Calendar")
        # Create the calendar with the callback
        calendar_component = streamlit_calendar(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            # key="calendar",
            # callbacks="eventClick",  # Add callback function
        )

    with col2:
        st.header("Event Details")
        parse_stcalendar_callback(calendar_component, format_calendar_data)


if __name__ == "__main__":
    show_calendar()
    # all_events = []
    # for k, c in color_dict.items():
    #     events = load_json(events_dir / f"{k}_events.json")
    #     for event in events:
    #         event["category"] = k
    #         event["backgroundColor"] = c
    #     all_events.extend(events)
