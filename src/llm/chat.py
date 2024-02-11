import sys
from pathlib import Path
import streamlit as st

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

from utils.placeholders import make_placeholder

# nqs
import logging
from utils.logging_setup import setup_logging
from utils.viz import (
    load_temp_plot,
)
from utils.errors import (
    DatabaseError,
    NetworkError,
    ArgumentParseError,
    handle_error,
)
from utils.placeholders import extract_placeholder
import prompts.engine as engine_prompts

# from utils.chat import Conversation
from llm import my_tools
from openai import OpenAI
import json
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from utils.viz import get_plotly_figure

# GPT_MODEL = "gpt-3.5-turbo-1106"
GPT_MODEL = "gpt-4-1106-preview"
JSON_MODEL = "gpt-4-1106-preview"

import time


### HANDLERS


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
        for message in self.streamlit_messages:
            # if message["role"] != "system" and message["role"] != "tool":
            # if message.role != "system" and message["role"] != "tool":
            # with st.chat_message(message["role"]):
            with st.chat_message(message.role):
                message.display()


class CerebraUser:
    def __init__(self, userid=None):
        self.userid = userid
        self.add_userid_if_missing()
        # set up logging
        setup_logging(__file__, self.userid)
        # set up tmp dir
        self.setup_tmp_dir()

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
        self.user = CerebraUser(userid)
        self.conversation = self.start_conversation()
        self.conversation.add_text_message("system", engine_prompts.system)
        self.backoff = True
        self.client = OpenAI()
        self.model = "gpt-4-1106-preview"
        self.stream_handler_class = PrintStreamHandler
        self.tool_module = my_tools

    def start_conversation(self):
        return Conversation()

    def completion_request(self, prompt):
        """
        This is where the main error handling is performed.
        This is also where I add in tools and some specificications for the run.
        """
        try:
            general_completion_request(
                self,
                prompt,
            )

        except Exception as e:
            raise
            err_msg_for_user = handle_error(e)
            self.respond_to_error(err_msg_for_user)

    def respond(self, text):
        stream_handler = self.stream_handler_class()
        for r in text:
            time.sleep(0.05)
            stream_handler.add_text(r)
        stream_handler.finish()
        self.conversation.add_obj_message(stream_handler)

    def respond_to_error(self, error_message):
        self.conversation.add_text_message("user", error_message)
        self.respond(error_message)


class StreamlitSession(Session):
    def __init__(self, userid):
        super().__init__(userid)
        self.stream_handler_class = StreamlitStreamHandler

    def start_conversation(self):
        return StreamlitConversation()


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
        def break_up(content):
            parts = []
            current_text = ""
            for element in content:
                if element["type"] == "text":
                    current_text += element["content"]
                elif element["type"] == "figure":
                    parts.append({"type": "text", "content": current_text})
                    parts.append(element)
                    current_text = ""
            if current_text:
                parts.append({"type": "text", "content": current_text})
            return parts

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


### CHATTING


def reprocess_chunks(session, content, placeholder):
    content_strings = [e["content"] for e in content]

    combined = "".join(content_strings)

    first_index = combined.find(placeholder)
    last_index = first_index + len(placeholder) - 1
    placeholder_indices = list(range(first_index, last_index + 1))

    # get first and last chunk index
    index_counter = 0
    for i, chunk in enumerate(content_strings):
        for char in chunk:
            if index_counter == first_index:
                first_chunk_index = i
            if index_counter == last_index:
                last_chunk_index = i
            index_counter += 1

    # get modified chunks
    index_counter = 0
    modified_chunks = []
    for i, chunk in enumerate(content_strings):
        new_chunk = ""
        for char in chunk:
            if i >= first_chunk_index or i <= last_chunk_index:
                if index_counter in placeholder_indices:
                    pass
                else:
                    new_chunk += char
            else:
                new_chunk += char
            index_counter += 1
        modified_chunks.append(new_chunk)

    # now make each chunk a dictionaru
    modified_chunks = [{"type": "text", "content": chunk} for chunk in modified_chunks]

    # add in figure
    modified_chunks.insert(
        last_chunk_index,
        {
            "type": "figure",
            "placeholder": placeholder,
            "content": session.figures[placeholder],
            # "content": load_temp_plot(session, placeholder),
        },
    )
    return modified_chunks


def get_tool_response(session, message):
    """
    This is where the value is retrieved
    """

    def get_value(data, key):
        # Check if data is a dictionary
        if isinstance(data, dict):
            return data.get(key, None)
        # Check if data is an object and has the attribute
        elif hasattr(data, key):
            return getattr(data, key, None)
        else:
            return None

    def call_function(function_name, all_args, userid):
        def extract_args_kwargs(function_name, all_args):
            for tool in session.tool_module.tools:
                if (
                    tool["type"] == "function"
                    and tool["function"]["name"] == function_name
                ):
                    # params = tool["function"]["parameters"]["properties"] # not needed now, could be useful for checking types
                    required_params = tool["function"]["parameters"].get("required", [])

                    # Extract args and kwargs
                    args = [
                        all_args[param]
                        for param in required_params
                        if param in all_args
                    ]
                    kwargs = {
                        k: v for k, v in all_args.items() if k not in required_params
                    }
                    return args, kwargs
            raise ValueError(f"Function {function_name} not found in tools.")

        args, kwargs = extract_args_kwargs(function_name, all_args)
        # args = [userid] + args
        func = getattr(session.tool_module, function_name)
        func_output = func(*args, **kwargs)
        return func_output

    def process_placeholder(content):
        if "plot" in content:
            placeholder = make_placeholder()
            fig = content["plot"]

            if not hasattr(session, "figures"):
                session.figures = {}
            session.figures[placeholder] = fig

            content["plot"] = placeholder

    tool_call = get_value(message, "tool_calls")[0]
    id = get_value(tool_call, "id")
    function = get_value(tool_call, "function")
    function_name = get_value(function, "name")

    arguments_string = get_value(function, "arguments")
    arguments = json.loads(arguments_string)

    # try:
    # except:
    #     raise Exception(f"Unable to parse arguments: {arguments_string}")

    content = call_function(function_name, arguments, session.user.userid)
    process_placeholder(content)

    content = str(content)

    tool_message = {
        "tool_call_id": id,
        "role": "tool",
        "name": function_name,
        "content": content,
    }
    return tool_message


def general_recombine(chunks, role="assistant"):
    """
    Role should be redefined but this works for now.
    """
    msg = {"role": role, "content": ""}
    # finish_reason = None
    for chunk in chunks:
        # if chunk.choices[0].finish_reason:
        # finish_reason = chunk.choices[0].finish_reason

        d = chunk.choices[0].delta
        if content := d.content:
            msg["content"] += content
        if d.tool_calls:
            if id := d.tool_calls[0].id:
                if not msg.get("tool_calls"):
                    msg["tool_calls"] = [{"id": id}]
                else:
                    msg["tool_calls"][0]["id"] = id
            if func_name := d.tool_calls[0].function.name:
                if not msg["tool_calls"][0].get("function"):
                    msg["tool_calls"][0]["function"] = {"name": func_name}
            if func_args := d.tool_calls[0].function.arguments:
                if not msg["tool_calls"][0].get("function"):
                    msg["tool_calls"][0]["function"] = {"arguments": func_args}
                else:
                    if not msg["tool_calls"][0]["function"].get("arguments"):
                        msg["tool_calls"][0]["function"]["arguments"] = func_args
                    else:
                        msg["tool_calls"][0]["function"]["arguments"] += func_args

    if msg["content"] == "":
        msg["content"] = None

    if msg.get("tool_calls"):
        msg["tool_calls"][0]["type"] = "function"

    return msg


class ChunkHandler:
    def __init__(self, session, completion_generator, delay=6):
        self.session = session
        self.completion_generator = completion_generator
        self.delay = delay
        self.first_chunk = next(completion_generator)
        self.is_tool = self.check_if_tool_response(self.first_chunk)
        self.raw_chunks = []
        self.message = self.session.stream_handler_class()  # message
        self.buffer_message = Message("assistant")
        self.buffer_index = 0

    def check_if_tool_response(self, chunk):
        if chunk.choices[0].delta.tool_calls:
            return True

    def stream_buffer(self, i):
        self.message.add_dict(self.buffer_message.content[i])

    def process_chunks(self):
        self.process_single_chunk(self.first_chunk)
        self.raw_chunks.append(self.first_chunk)
        if self.is_tool:
            self.process_tool_chunks()
        else:
            self.process_assistant_chunks()
        message = general_recombine(self.raw_chunks)
        logging.info(f"message: {message}")

    def process_single_chunk(self, chunk):
        """
        I need to keep track of a few things.
        A response is ready to be printed/processed when (i>=delay -->chunk[i-delay])
        then I need to add
        """

        def split_content(elements):
            for i, element in enumerate(elements[::-1]):
                if element.get("placeholder"):
                    break
            return elements[: -i + 1], elements[-i + 1 :]

        def parse_buffer():
            # split up the content at any previous placeholders and adjust the buffer content
            # logging.info(f"pre buff message: {self.buffer_message.content}")
            inactive_content, active_content = split_content(
                self.buffer_message.content
            )
            active_message_text = "".join([e["content"] for e in active_content])
            if placeholder := extract_placeholder(active_message_text):
                self.buffer_index += 1
                active_content = reprocess_chunks(
                    self.session, active_content, placeholder
                )
            self.buffer_message.content = inactive_content + active_content
            # logging.info(f"post buff message: {self.buffer_message.content}")

        # add to buffer
        content = chunk.choices[0].delta.content
        if isinstance(content, str):
            self.buffer_message.add_text(content)
            parse_buffer()

    # """
    #     chunks = 10
    #     delay  = 4
    #     for 0-9, first process: 4, 5, 6, 7, 8, 9
    #     so stream_buffer 0,1,2,3,4,5
    #     for i range(10-4, 10)=range(6,10)
    #     for in rang
    # """
    def process_assistant_chunks(self):
        for i, chunk in enumerate(self.completion_generator):
            if chunk.choices[0].finish_reason == "stop":
                break
            i += 1  # since first chunk is already processed
            self.raw_chunks.append(chunk)
            self.process_single_chunk(chunk)
            if i >= self.delay:
                # stream the buffer
                self.stream_buffer(i - self.delay)
                # display up to this point

        # process after delay
        for i in range(len(self.raw_chunks) - self.delay, len(self.raw_chunks)):
            self.process_single_chunk(self.raw_chunks[i])
            self.stream_buffer(i)

        # process leftover buffer
        for i in range(-self.buffer_index, 0):
            self.stream_buffer(i)

        logging.info(f"buffer length: {len(self.buffer_message.content)}")
        logging.info(f"length of raw chunks: {len(self.raw_chunks)}")

        # finish and add message to the conversation
        self.message.finish()
        self.session.conversation.add_obj_message(self.message)

    def process_tool_chunks(self):
        for i, chunk in enumerate(self.completion_generator):
            i += 1  # since first chunk is already processed
            self.raw_chunks.append(chunk)

        message = general_recombine(self.raw_chunks)
        self.session.conversation.add_tool_response(message)  # make different func
        tool_response = get_tool_response(self.session, message)
        self.session.conversation.add_tool_return(tool_response)


def process_completion(session, **input_completions_kwargs):
    def prepare_completion_generator(session, **input_completions_kwargs):
        # refine args/kwargs
        completions_kwargs = {
            "model": session.model,
            "messages": getattr(session.conversation, "messages", None),
            "stream": True,
            "tools": getattr(session.tool_module, "tools", None),
        }
        completions_kwargs.update(input_completions_kwargs)
        client = session.client

        # can I make this less clunky?
        if session.backoff:

            @retry(
                wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6)
            )
            def completion_func():
                return client.chat.completions.create(**completions_kwargs)
        else:

            def completion_func():
                return client.chat.completions.create(**completions_kwargs)

        return completion_func()

    def parse_stream(
        session,
        completion,
    ):
        """
        When I process a chunk, I need to do the following things.
        First, I need to see whether it is a tool response.
        If it is a tool response, I skip over most of the processing.
        For non-tool response, I print out the message.
        """

        # intialize stream handler
        # stream_handler = session.stream_handler_class()
        # get the first chunk and see if it is a tool response
        chunk_handler = ChunkHandler(session, completion, delay=4)
        chunk_handler.process_chunks()

    # get completion generator
    completion_generator = prepare_completion_generator(
        session, **input_completions_kwargs
    )
    # now parse the stream
    parse_stream(session, completion_generator)


def general_completion_request(
    session,
    prompt=None,
    **input_completions_kwargs,
):
    """
    Any extra kwargs will go into the api call.
    This is where the request is made; handle_steam_completion is where the response is parsed.
    The placeholder is generated when a tool response is parsed.
    The placeholder is extracted when the assistant response to the tool is parsed.
    """

    if prompt:
        session.conversation.add_text_message("user", prompt)

    logging.info(f"Conversation (Pre-Completion): {session.conversation.messages}")

    # parse completion
    process_completion(session, **input_completions_kwargs)

    # determine if resubmit; can further specify resubmit conditions
    if session.conversation.messages[-1]["role"] == "tool":
        general_completion_request(
            session,
            **input_completions_kwargs,
        )


#### simple

helicone_info = {
    "api_key": "sk-345rsyy-cxiemia-ve5mdoy-j7p2k7i",
    "base_url": "https://oai.hconeai.com/v1",
    "default_headers": {
        "Helicone-Auth": f"Bearer sk-345rsyy-cxiemia-ve5mdoy-j7p2k7i",
    },
}


def json_request_prompt_only(
    prompt, model=JSON_MODEL, role="user", load=True, **completions_kwargs
):
    # from helicone.openai_async import openai
    # client = OpenAI(**helicone_info)

    messages = [{"role": role, "content": prompt}]
    return json_request(messages, model=model, load=load, **completions_kwargs)
    # return json.loads(content)


def json_request(messages, model=JSON_MODEL, load=True, **completions_kwargs):
    import json

    from openai import OpenAI

    client = OpenAI()
    # messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        **completions_kwargs,
    )
    content = response.choices[0].message.content
    if load:
        return json.loads(content)
    else:
        return content


def get_completion(prompt, model=GPT_MODEL, response_format=None):
    client = OpenAI()
    messages = [{"role": "user", "content": prompt}]
    print(response_format)
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0, response_format=response_format
    )
    return response.choices[0].message.content


def fake_respond(prompt, session):
    stream_handler = session.stream_handler_class()
    fig = get_plotly_figure()
    session.conversation.add_text_message("user", prompt)

    full_response = ""
    for r in prompt:
        full_response += r
        time.sleep(0.05)
        stream_handler.add_text(r)
    stream_handler.add_figure(fig)
    stream_handler.finish()
    session.conversation.add_obj_message(stream_handler)
