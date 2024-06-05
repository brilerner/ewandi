import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src": p = p.parent
sys.path.append(str(p))


import streamlit as st

from pathlib import Path
import time
from llm.chat import EwandiUserSession, ewandi_completion_request

from utils.plot import get_plotly_figure
# from openai import OpenAI

# client = OpenAI()

# def plot_to_streamlit(plot):
# st.plotly_chart(plot)

# if "messages" not in session:
#     # st.write("Resetting messages")
#     session.messages = []
# # if "user_id" not in session:
#     # session["user_id"] = "brian"
# # if "client" not in session:
#     # session["client"] = OpenAI()
# if "backoff" not in session:
#     session["backoff"] = True


def respond(prompt, stream_handler, session):
    full_response = ""
    for r in prompt:
        time.sleep(0.2)
        full_response += r
        stream_handler.markdown(full_response + "▌")
    stream_handler.markdown(full_response)

    session.messages.append({"role": "assistant", "content": full_response})


if "session" not in st.session_state:
    st.session_state["session_started"] = True
    st.session_state["session"] = EwandiUserSession("brian")
    session = st.session_state["session"]
else:
    session = st.session_state["session"]
    # st.write("Resetting messages")
    # st.session_state.messages = []
# session = st.session_state

for message in session.messages:
    if message["role"] != "system" and message["role"] != "tool":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Enter a message"):
    session.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.container()...
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        respond(prompt, message_placeholder, session)


# def simple_response(stream_handler):


#     for response in client.chat.completions.create(
#         model=session["openai_model"],
#         messages=[
#             {"role": m["role"], "content": m["content"]}
#             for m in session.messages
#         ],
#         stream=True,
#     ):
#         full_response += response.choices[0].delta.content or ""
#         message_placeholder.markdown(full_response + "▌")
#     message_placeholder.markdown(full_response)
# session.messages.append({"role": "assistant", "content": full_response})

# with st.chat_message("assistant"):
#     message_placeholder = st.empty()
#     # run request
#     message = ewandi_completion_request(
#         session,
#         # session.session,
#         stream_handler=message_placeholder.markdown,
#         plot_handler=plot_to_streamlit,
#     )
# session.messages.append(message)

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
