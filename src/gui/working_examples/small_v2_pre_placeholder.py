import sys
from pathlib import Path

# root_path = str(Path(__file__).resolve().parent.parent)
root_path = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(root_path)


import streamlit as st

from pathlib import Path
import time
# from llm.chat import EwandiUserSession, ewandi_completion_request

from utils.viz import get_plotly_figure
import prompts.engine as engine_prompts
from openai import OpenAI


class Message:
    """
    Creates a message.
    Each message is a dictionary with role and content keys.
    The content value is a list of dicts, each of which has a type and content key.
    The order of the list determines the order of the elements in the message.
    A message can include text, figures, and other elements.
    It is independent of the display method.
    """

    def __init__(self, role, first_text=None):
        self.role = role
        self.content = []
        if first_text:
            self.add_text(first_text)

    def add_text(self, text):
        self.content.append({"type": "text", "content": text})

    def add_figure(self, figure):
        self.content.append({"type": "figure", "content": figure})

    def display(self):
        for element in self.content:
            if element["type"] == "text":
                print(element["content"], end="")
            elif element["type"] == "figure":
                element["content"].show()

    # I need to figure out how to handle this with plots
    def api_message(self):
        text_elements = [e["content"] for e in self.content if e["type"] == "text"]
        full_text = "".join(text_elements)
        return {"role": self.role, "content": full_text}

    # def __repr__(self):
    #     return f"{self.role}: {self.content}"

    # def __str__(self):
    #     return f"{self.role}: {self.content}"

    # def __dict__(self):
    #     return {"role": self.role, "content": self.content}

    # def __getitem__(self, key):
    #     return self.__dict__()[key]


class StreamlitMessage(Message):
    """
    Creates a message.
    Each message is a dictionary with role and content keys.
    The content value is a list of dicts, each of which has a type and content key.
    The order of the list determines the order of the elements in the message.
    A message can include text, figures, and other elements.
    It is independent of the display method.
    This subclass also deals with handling plots...
    """

    def __init__(self, role, first_text=None):
        super().__init__(role, first_text)
        # self.full_message = {"role": role, "content": content}
        # self.content = self.message["content"]  # for convenience

    # def add_text(self, text):
    #     self.content.append({"type": "text", "content": text})
    def add_text(self, text):
        # I need to figure out how to update the last text message
        if self.content and self.content[-1]["type"] == "text":
            self.content[-1]["content"] += text
            # self.content[-1]["content"] = text
        else:
            self.content.append({"type": "text", "content": text})

    def add_figure(self, figure):
        self.content.append({"type": "figure", "content": figure})

    def display(self):
        # with st.container(): # NECESSAry? cl
        for element in self.content:
            if element["type"] == "text":
                st.markdown(element["content"])
            elif element["type"] == "figure":
                st.plotly_chart(element["content"])

    def streamlit_message(self):
        return {"role": self.role, "content": self.content}


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

    def add_tool_response(self, name, content):
        # TBD
        pass

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
            if type(message) != dict:
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
        self.streamlit_messages.append(message)
        self.messages.append(message.api_message())

    def display(self):
        """
        I've previously filtered out the messages that are not system or tool.
        """
        for message in self.streamlit_messages:
            # if message["role"] != "system" and message["role"] != "tool":
            # if message.role != "system" and message["role"] != "tool":
            # with st.chat_message(message["role"]):
            with st.chat_message(message.role):
                message.display()

        # if role == "system":
        #     pass
        #     # self._add_system(text)
        # elif role == "user":
        #     self._add_user(text)
        # elif role == "assistant":
        #     self._add_assistant(text)
        # elif role == "tool":
        #     print("Wrong function for adding tool message. Use add_tool_response")
        #     raise Exception

    # def add_tool_response(self, name, content):
    #     # self.messsages.append(...)
    #     pass

    # def _add_system(self, text):
    #     self.messages.append({"role": "system", "content": text})

    # def _add_user(self, text):
    #     # create a message
    #     message = StreamlitMessage("user", text)
    #     # add to streamlit messages
    #     self.streamlit_messages.append(message)

    # def _add_assistant(self, text):
    #     message = StreamlitMessage("assistant", text)
    #     self.streamlit_messages.append(message)

    # def _convert_message(self, message):
    #     for element in message.content:
    #         if element["type"] == "text":
    #             pass
    #         elif element["type"] == "figure":
    #             pass


class EwandiUser:
    def __init__(self, userid=None):
        self.userid = userid
        self.add_userid_if_missing()
        # set up logging
        # setup_logging(__file__, self.userid)
        # set up tmp dir
        # self.setup_tmp_dir()

    def add_userid_if_missing(self):
        def generate_userid():
            import uuid

            return str(uuid.uuid4())[:8]

        if not self.userid:
            self.userid = generate_userid()

    def setup_tmp_dir(self):
        save_dir = Path(root_path) / "tmp" / self.userid / "plots"
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)


class Session:
    def __init__(self, userid):
        self.user = EwandiUser(userid)
        self.conversation = self.start_conversation()
        self.conversation.add_text_message("system", engine_prompts.system)
        self.backoff = True
        self.client = OpenAI()

    def start_conversation(self):
        return Conversation()


class StreamlitSession(Session):
    def __init__(self, userid):
        super().__init__(userid)

    def start_conversation(self):
        return StreamlitConversation()


def set_streamlit_session():
    if "session" not in st.session_state:
        st.session_state["session"] = StreamlitSession("brian")
        session = st.session_state["session"]
    else:
        session = st.session_state["session"]
    return session


class StreamlitStreamHandler(StreamlitMessage):
    """
    This function is used each time an assistant message is expected from the API call.
    As the stream is processed, the current message needs to be updated, and when the stream is finished, the message needs to be added to the conversation.
    There is clearly some overlap between this and the StreamlitConversation class.

    """

    def __init__(self):
        super().__init__("assistant")
        self.streamlit_container = st.empty()
        self.in_progress_symb = "▌"
        # self.message = StreamlitMessage("assistant")

    def add_text(self, text):
        super().add_text(text)
        self._update()

    def add_figure(self, figure):
        super().add_figure(figure)
        self._update()

    def _update(self):
        self.streamlit_container.empty()
        # adding small sleep seems to be nec: see https://discuss.streamlit.io/t/using-st-empty/29509
        time.sleep(0.0001)  # necessart
        # time.sleep(2)  # necessart
        with self.streamlit_container.container():
            self.display()

    def display(self):
        # with st.container(): # NECESSAry? cl
        for i, element in enumerate(self.content):
            if element["type"] == "text":
                if i == len(self.content) - 1:
                    st.markdown(element["content"] + self.in_progress_symb)
                else:
                    st.markdown(element["content"])
            elif element["type"] == "figure":
                st.plotly_chart(element["content"])

    def finish(self):
        self.streamlit_container.empty()
        time.sleep(0.01)  # necessart
        with self.streamlit_container.container():
            super().display()

    # def start(self):
    #     return self.


def respond(prompt, stream_handler, session):
    fig = get_plotly_figure()
    # firs things first: add the user message to the conversation
    session.conversation.add_text_message("user", prompt)

    full_response = ""
    for r in prompt:
        full_response += r
        time.sleep(0.05)
        # update the display output
        # stream_handler.add_text(full_response)
        stream_handler.add_text(r)
    stream_handler.add_figure(fig)
    stream_handler.finish()
    # I now have the content in a list of message objects
    # I want add these to to the streamlit conversation and the msg history
    # assistant is different since images might be included. I need to account for this placeholder
    session.conversation.add_obj_message(stream_handler)
    # session.conversation.append(stream_handler.message()) # add the message to the convo
    # session.conversation.add_text_message("assistant", full_response)


# """
# Here, I want to loop through the containers for each message. Each container can contain both figures and images. I want to be able to display both of these.
# {"role":role, "content":[containers]} # for the streamlit streaming, the content needs to be a list of elements

# """

default_prompt = "Here's the first prompt"

# initialize the conversation history
session = set_streamlit_session()
# display the previous messages
session.conversation.display()

user_input = st.chat_input("Enter a message")

if "first_prompt_completed" in st.session_state:
    prompt = user_input
else:
    prompt = default_prompt
    st.session_state["first_prompt_completed"] = True


if prompt:
    # if prompt := st.chat_input("Enter a message"):
    # display_user_message(prompt)

    with st.chat_message("user"):
        with st.container():
            st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.container():
            stream_handler = StreamlitStreamHandler()  # auto initialized as assistant
            respond(prompt, stream_handler, session)


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
