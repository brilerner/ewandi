import streamlit as st

st.set_page_config(layout="wide")

from streamlit_calendar import calendar

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
        font-size: 2rem;
    }
"""


def format_event_data(event_data):
    formatted_data = f"**Event Title:** {event_data.get('title')}\n\n"
    formatted_data += f"**Start Time:** {event_data.get('start')}\n"
    formatted_data += f"**End Time:** {event_data.get('end')}\n"
    return formatted_data



def parse_callback(calendar_component):

    if calendar_component.get("callback", "") == "eventClick":
        cb = calendar_component.get("eventClick")
        event = cb["event"]
        st.markdown("# Event Details:")
        st.markdown(format_event_data(event))

def show_calendar_with_output():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Calendar")
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


if __name__ == "__main__":
    show_calendar_with_output()

# Create a space to display event details

# Display the calendar


# st.write(str(st.session_state))
# if calendar_component.get("eventClick") is not None:
#     event_details.markdown("Event Details:")
# st.session_state["events"] = state["eventsSet"]

# # Display event details underneath the calendar
# if event_details:
#     event_data = event_details.json()
#     if event_data:
#         st.write("Event Details:")
#         st.write(event_data)
