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

from utils.io import load_json
from viz.plot import plot_events
from llm.chat import CerebraUserSession, cerebra_completion_request
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


#### main tabs


def show_chatbot_tab():

    
    def streamlit_plot_handler(plot):
        st.plotly_chart(plot)

    def get_streamlit_stream_handler():
        message_placeholder = st.empty()
        def _(content):
            return message_placeholder.markdown(content)
        return _


    if "session" not in st.session_state:
        st.session_state["session_started"] = True
        st.session_state["session"] = CerebraUserSession("brian")
        session = st.session_state["session"]
    else:
        session = st.session_state["session"]

    # for message in st.session_state.session.conversation.get_display_messages():
    for message in session.messages:
        if message["role"] != "system" and message["role"] != "tool":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # opener = prompts.engine.get_opener()
    # opener = random.choice(openers)
    opener = "Enter"
    if prompt := st.chat_input(opener):

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            

            # run request
            cerebra_completion_request(
                prompt,
                session,
                stream_handler=message_placeholder,
                plot_handler=plot_to_streamlit,
            )

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

show_chatbot_tab()

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
