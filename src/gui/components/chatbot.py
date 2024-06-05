import streamlit as st
from streamlit_setup import set_streamlit_session


def show_chatbot():
    # initialize the conversation history
    debug = False
    # debug = True
    session = set_streamlit_session(debug=debug)

    # default_prompt = "How many times did I have computer programming homework?"
    default_prompt = None
    if default_prompt:
        user_input = st.chat_input("Enter a message")
        if "first_prompt_completed" in st.session_state:
            prompt = user_input
        else:
            prompt = default_prompt
            st.session_state["first_prompt_completed"] = True
    else:
        prompt = st.chat_input("Enter a message")

    # display the previous messages
    session.conversation.display()

    if prompt:
        with st.chat_message("user"):
            with st.container():
                st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.container():
                # respond(prompt, session)
                session.completion_request(prompt)
