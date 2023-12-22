import streamlit as st
import plotly.express as px
import time
import random
from openai import OpenAI

import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')
from utils.viz import get_plotly_figure
import prompts.engine as PROMPTS

from llm.chat import chat_completion_request, Conversation
from tools.tools import tools, call_function

import logging

client = OpenAI()
# MODEL_NAME = 'gpt-3.5-turbo'
# # MODEL_NAME = 'gpt-4'

MODEL_NAME = "gpt-3.5-turbo-0613"
STREAM=True

logging.info("--------------------------- NEW RUN ------------------------------------------------------")

def main():


    logging.info("Starting CerebraChat")
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Choose a Tab", 
        [
            "Overview", 
            "CerebraChat",
        ],
        index=1
    )

    if choice == "Overview":
        show_overview_tab()
    if choice == "CerebraChat":
        # st.write("Chatbot Placeholder")
        show_chatbot_tab()


def show_chatbot_tab():


    conversation = Conversation(first_message = ("system", PROMPTS.system))
    # conversation.add_message("system", PROMPTS.system)

    for message in conversation.messages:
        if type(message) != dict:
            message = dict(message)
        logging.info(f"check role: {message}")
        if message["role"] != "system" and message["role"] != "tool" :
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    with st.chat_message("user"):
        st.write("How many occurrences of Basketball Game are there?")

    # Accept user input; uses walrus operator
    # if prompt := st.chat_input(PROMPTS.opener):
        # if prompt == "q":
        #     prompt = "How many occurrences of Basketball Game are there?"
        # conversation.messages.append({"role": "user", "content": prompt})
        
    testing = True
    if testing:
        prompt = "How many occurrences of Basketball Game are there?"
        conversation.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)


        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            if STREAM:
                for response in chat_completion_request(conversation, model=MODEL_NAME, tools=tools, stream=STREAM):
                    full_response += (response.choices[0].delta.content or "")
                    # logging.info(f"full response: {full_response}")
                    message_placeholder.markdown(full_response + "▌")
                    # time.sleep(0.1)
            else:
                    response = chat_completion_request(conversation, model=MODEL_NAME, tools=tools, stream=STREAM)
                    logging.info("non steam response in app.py: " + str(response))
                    full_response = response.choices[0].message.content 
                    # logging.info(f"full response: {full_response}")
                    # message_placeholder.markdown(full_response + "▌")
                    # time.sleep(0.1)     
            message_placeholder.markdown(full_response)
                
        # plot chart to test
        # st.plotly_chart(get_plotly_figure(), use_container_width=True)

def show_overview_tab():

    st.header("Overview")
    
    st.plotly_chart(get_plotly_figure(), use_container_width=True)

if __name__ == "__main__":
    main()
