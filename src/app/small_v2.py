import sys
from pathlib import Path

# root_path = str(Path(__file__).resolve().parent.parent)
root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)


import streamlit as st

from pathlib import Path
import time

import prompts.engine as engine_prompts
from utils.errors import (
    DatabaseError,
    NetworkError,
    ArgumentParseError,
    handle_error,
)
from llm import my_tools
from llm.chat import StreamlitSession


def set_streamlit_session():
    if "session" not in st.session_state:
        st.session_state["session"] = StreamlitSession("brian")
        session = st.session_state["session"]
    else:
        session = st.session_state["session"]
    return session


# initialize the conversation history
session = set_streamlit_session()
# display the previous messages
session.conversation.display()

# set up first prmpt
user_input = st.chat_input("Enter a message")
# default_prompt = "Here's the first prompt"
# default_prompt = "Please tell me a joke."
default_prompt = "What is my average sleep?"
if "first_prompt_completed" in st.session_state:
    prompt = user_input
else:
    prompt = default_prompt
    st.session_state["first_prompt_completed"] = True


if prompt:
    with st.chat_message("user"):
        with st.container():
            st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.container():
            # respond(prompt, session)
            session.completion_request(prompt)
