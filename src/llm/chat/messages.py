import sys
from pathlib import Path
p = Path(__file__).resolve()
while p.name != 'src':
    p = p.parent
sys.path.append(str(p))

import streamlit as st
import time

from llm.chat.chatutils import break_up




class Message:
    """
    Creates a message.
    Each message is a dictionary with role and content keys.
    The content value is a list of dicts, each of which has a type and content key.
    The order of the list determines the order of the elements in the message.
    A message can include text, figures, and other elements.
    It is independent of the display method.
    """

    def __init__(self, role, first_text=None, show=True):
        self.role = role
        self.content = []
        if first_text:
            self.add_text(first_text)
        self.show = show

    def add_text(self, text):
        self.content.append({"type": "text", "content": text})

    def add_figure(self, figure, placeholder=None):
        self.content.append(
            {"type": "figure", "content": figure, "placeholder": placeholder}
        )

    def add_dict(self, dict):
        self.content.append(dict)

    def display(self):
        for element in self.content:
            if element["type"] == "text":
                print(element["content"], end="")
            elif element["type"] == "figure":
                if self.show:
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

    def add_figure(self, figure, placeholder=None):
        self.content.append(
            {"type": "figure", "content": figure, "placeholder": placeholder}
        )

    def add_dict(self, dict):
        self.content.append(dict)

    def display(self):
        # with st.container(): # NECESSAry? cl
        for element in self.content:
            if element["type"] == "text":
                st.markdown(element["content"])
            elif element["type"] == "figure":
                st.plotly_chart(element["content"])

    def streamlit_message(self):
        return {"role": self.role, "content": self.content}


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

    # can I integrate with "core handler" later?
    def add_text(self, text):
        super().add_text(text)
        self._update()

    def add_figure(self, figure, placeholder=None):
        super().add_figure(figure, placeholder=placeholder)
        self._update()

    def add_dict(self, dict):
        super().add_dict(dict)
        self._update()

    def _update(self, finish=False):
        self.streamlit_container.empty()
        # adding small sleep seems to be nec: see https://discuss.streamlit.io/t/using-st-empty/29509
        time.sleep(0.000001)  # necessart
        # time.sleep(2)  # necessart
        with self.streamlit_container.container():
            self.display(finish=finish)

    def display(self, finish=False):
        # with st.container(): # NECESSAry? clreak
        

        content_to_display = break_up(self.content)

        if finish:
            pass
        else:
            if content_to_display:
                if content_to_display[-1]["type"] == "text":
                    content_to_display[-1]["content"] += self.in_progress_symb
            else:
                content_to_display = [
                    {"type": "text", "content": self.in_progress_symb}
                ]

        for i, element in enumerate(content_to_display):
            # for i, element in enumerate(self.content):
            if element["type"] == "text":
                st.markdown(element["content"])
                # if i == len(content_to_display) - 1:
                #     st.markdown(element["content"] + self.in_progress_symb)
                # else:
                #     st.markdown(element["content"])
            elif element["type"] == "figure":
                st.plotly_chart(element["content"])

    def finish(self):
        self._update(finish=True)


class PrintStreamHandler(Message):
    """
    This function is used each time an assistant message is expected from the API call.
    As the stream is processed, the current message needs to be updated, and when the stream is finished, the message needs to be added to the conversation.
    There is clearly some overlap between this and the StreamlitConversation class.

    """

    def __init__(self):
        super().__init__("assistant")

    def add_text(self, text):
        super().add_text(text)
        self._update()

    def add_figure(self, figure, placeholder=None):
        super().add_figure(figure, placeholder=placeholder)
        self._update()

    def _update(self):
        self.display()

    def add_dict(self, dict):
        super().add_dict(dict)
        self._update()

    def display(self):
        current = self.content[-1]
        if current["type"] == "text":
            print(current["content"], end="")
        elif current["type"] == "figure":
            current["content"].show()

    def finish(self):
        pass

# class CoreStreamHandler(Message):
#     """
#     Needs to used by Streamlit or Print classes

#     """

#     def __init__(self):
#         super().__init__("assistant")

#     def add_text(self, text):
#         super().add_text(text)
#         self._update()

#     def add_figure(self, figure):
#         super().add_figure(figure)
#         self._update()