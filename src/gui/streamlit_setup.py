import streamlit as st
from utils.errors import (
    DatabaseError,
    NetworkError,
    ArgumentParseError,
    handle_error,
)

# from llm import my_tools
from llm.chat import StreamlitSession


def set_streamlit_session(debug=False):
    if "session" not in st.session_state:
        st.session_state["session"] = StreamlitSession("brian", debug=debug)
        session = st.session_state["session"]
    else:
        session = st.session_state["session"]
    return session
