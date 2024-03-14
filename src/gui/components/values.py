import streamlit as st

from llm.my_tools.plotting import plot_multiple_event_count, plot_multiple_values

from utils.io import load_json
from gui.streamlit_setup import sleep_events, survey_events


def show_sleep():
    fig = plot_multiple_values(sleep_events)
    st.plotly_chart(fig)


def show_survey():
    fig = plot_multiple_values(survey_events)
    st.plotly_chart(fig)
