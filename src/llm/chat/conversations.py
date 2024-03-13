
import sys
from pathlib import Path
p = Path(__file__).resolve()
while p.name != 'src':
    p = p.parent
sys.path.append(str(p))

import streamlit as st
from llm.chat.messages import Message, StreamlitMessage
from llm.chat.chatutils import break_up

class Conversation:
    """
    Creates a conversation that is used as an argument for the OpenAI API call.
    First message is a system message.
    Only system and user should use add_text_message.
    Assistant and tool should be formatted correctly upon return of the API call.
    """

    def __init__(self):
        self.messages = []

    def add_text_message(self, role, content):
        message = {"role": role, "content": content}
        self.messages.append(message)

    def add_obj_message(self, message):
        self.messages.append(message.api_message())

    def add_tool_response(self, tool_response):
        self.messages.append(tool_response)

    def add_tool_return(self, tool_response):
        self.messages.append(tool_response)

    def get_display_messages(self):
        messages_to_display = []
        for message in self.messages:
            # logging.info(f"message : {message}")
            if not isinstance(message, dict):
                message = dict(message)
            if message["role"] != "system" and message["role"] != "tool":
                # logging.info(f"message : {message}")
                messages_to_display.append(message)
        return messages_to_display

    def display(self):
        from termcolor import colored

        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "tool": "magenta",
        }

        for message in self.messages:
            if not isinstance(message, dict):
                message = dict(message)
            if message["role"] == "system":
                print(
                    colored(
                        f"system: {message['content']}\n",
                        role_to_color[message["role"]],
                    )
                )
            elif message["role"] == "user":
                print(
                    colored(
                        f"user: {message['content']}\n", role_to_color[message["role"]]
                    )
                )
            elif message["role"] == "assistant" and message.get("function_call"):
                print(
                    colored(
                        f"assistant: {message['function_call']}\n",
                        role_to_color[message["role"]],
                    )
                )
            elif message["role"] == "assistant" and not message.get("function_call"):
                print(
                    colored(
                        f"assistant: {message['content']}\n",
                        role_to_color[message["role"]],
                    )
                )
            elif message["role"] == "tool":
                print(
                    colored(
                        f"function ({message['name']}): {message['content']}\n",
                        role_to_color[message["role"]],
                    )
                )


class StreamlitConversation(Conversation):
    """
    Extends the Conversation class to properly format/filter messages for display in Streamlit.
    """

    def __init__(self):
        super().__init__()
        self.streamlit_messages = []

    def add_text_message(self, role, text):
        super().add_text_message(role, text)
        message = StreamlitMessage(role, text)
        if role in ["user", "assistant"]:
            self.streamlit_messages.append(message)

    def add_obj_message(self, message):
        super().add_obj_message(message)
        self.streamlit_messages.append(message)

    def display(self):
        """
        I've previously filtered out the messages that are not system or tool.
        """
        messages_to_display = self.streamlit_messages

        # for message in self.streamlit_messages:
        for message in messages_to_display:
            with st.chat_message(message.role):

                for element in break_up(message.content):
                    if element["type"] == "text":
                        st.markdown(element["content"])
                    elif element["type"] == "figure":
                        st.plotly_chart(element["content"])

            # if message["role"] != "system" and message["role"] != "tool":
            # if message.role != "system" and message["role"] != "tool":
            # with st.chat_message(message["role"]):
                # message.display()
                # st.write("hello")
                # message.display()