import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src":
    src_dir = src_dir.parent
sys.path.append(str(src_dir))


import streamlit as st

# st.set_page_config(layout="wide", page_title="Ewandi Demo")
import numpy as np
import pandas as pd
from pathlib import Path

import prompts
from gui.display_msgs import intro
from streamlit_setup import bio_text, imgs_dir
from components import show_chatbot, show_calendar, show_sleep, show_survey


def show_overview_tab():
    st.header("Overview")
    st.write("Welcome to Ewandi...")
    st.write(intro)


def show_bio_tab():
    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        img_path = imgs_dir / "llm.png"
        st.image(str(img_path))

    with col2:
        st.header("Len's Bio")
        st.write(bio_text)


def show_dataset_tab():
    st.header("Available Data")

    tabs = [
        "Calendar Hub",
        "Sleep Tracker",
        "End-of-Day Survey",
    ]

    tab1, tab2, tab3 = st.tabs(tabs)

    with tab1:
        show_calendar()

    with tab2:
        show_sleep()

    with tab3:
        show_survey()


def main():
    tabs = [
        "Overview",
        "Learn about Len",
        "Explore the Data",
        "Chat with Ewandi",
    ]

    tab_funcs = [
        show_overview_tab,
        show_bio_tab,
        show_dataset_tab,
        show_chatbot,
    ]

    choice = st.sidebar.radio("Choose a Tab", tabs)

    for i, t in enumerate(tabs):
        if choice == t:
            tab_funcs[i]()


if __name__ == "__main__":
    main()
