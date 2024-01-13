import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)


import streamlit as st

st.set_page_config(layout="wide", page_title="Cerebra Demo")
from pathlib import Path
from utils.general import get_root
from llm.chat import start_cerebra_session, cerebra_completion_request
from openai import OpenAI

client = OpenAI()
# import logging

profile = "llm_v1"
imgs_dir = Path(__file__).resolve().parent / "imgs"
events_dir = (
    get_root() / "data" / "sim" / "profiles" / profile / "outputs" / "streamlit"
)


def plot_to_streamlit(plot):
    st.plotly_chart(plot)


if "messages" not in st.session_state:
    # st.write("Resetting messages")
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "brian"
if "client" not in st.session_state:
    st.session_state["client"] = OpenAI()
if "backoff" not in st.session_state:
    st.session_state["backoff"] = True
# display non-tool messages
# for message in st.session_state.session.conversation.get_display_messages():
for message in st.session_state.messages:
    # if message["role"] != "system" and message["role"] != "tool":
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

opener = random.choice("Question")
if prompt := st.chat_input(opener):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # st.session_state.session.conversation.messages.append(
    #     {"role": "user", "content": prompt}
    # )

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
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # with st.chat_message("assistant"):
    #     message_placeholder = st.empty()
    #     # run request
    #     message = cerebra_completion_request(
    #         st.session_state,
    #         # st.session_state.session,
    #         stream_handler=message_placeholder.markdown,
    #         plot_handler=plot_to_streamlit,
    #     )
    # st.session_state.messages.append(message)

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
