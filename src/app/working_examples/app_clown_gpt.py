import streamlit as st
import plotly.express as px
import time
import random
from openai import OpenAI

import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))
from utils.viz import get_plotly_figure
import prompts.clowngpt as PROMPTS

client = OpenAI()
MODEL_NAME = "gpt-3.5-turbo"


def main():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Choose a Tab",
        [
            "Overview",
            "CerebraChat",
        ],
        index=1,
    )

    if choice == "Overview":
        show_overview_tab()
    if choice == "CerebraChat":
        # st.write("Chatbot Placeholder")
        show_chatbot_tab()


def show_chatbot_tab():
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = MODEL_NAME

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": PROMPTS.system}]

    # Omit system messages from chat history
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input(PROMPTS.opener):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.content or ""
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
        # plot chart to test
        st.plotly_chart(get_plotly_figure(), use_container_width=True)


def show_overview_tab():
    st.header("Overview")

    st.plotly_chart(get_plotly_figure(), use_container_width=True)


if __name__ == "__main__":
    main()
