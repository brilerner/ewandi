import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))


import streamlit as st

from pathlib import Path
import time
from llm.chat import start_cerebra_session, cerebra_completion_request
# from openai import OpenAI

# client = OpenAI()

# def plot_to_streamlit(plot):
# st.plotly_chart(plot)
response = "This is a test response"

if "messages" not in st.session_state:
    # st.write("Resetting messages")
    st.session_state.messages = []
# if "user_id" not in st.session_state:
# st.session_state["user_id"] = "brian"
# if "client" not in st.session_state:
# st.session_state["client"] = OpenAI()
if "backoff" not in st.session_state:
    st.session_state["backoff"] = True

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter a message"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for r in prompt:
            time.sleep(0.2)
            full_response += r
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #     for response in client.chat.completions.create(
    #         model=st.session_state["openai_model"],
    #         messages=[
    #             {"role": m["role"], "content": m["content"]}
    #             for m in st.session_state.messages
    #         ],
    #         stream=True,
    #     ):
    #         full_response += response.choices[0].delta.content or ""
    #         message_placeholder.markdown(full_response + "▌")
    #     message_placeholder.markdown(full_response)
    # st.session_state.messages.append({"role": "assistant", "content": full_response})

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
