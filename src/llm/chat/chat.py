import sys
from pathlib import Path
import streamlit as st


src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from utils.placeholders import make_placeholder

# nqs
import logging
from utils.viz import (
    load_temp_plot,
)

from utils.placeholders import extract_placeholder


# from utils.chat import Conversation
from llm.chat.messages import Message
from openai import OpenAI
import json
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from utils.viz import get_plotly_figure

import plotly.io as pio

# GPT_MODEL = "gpt-3.5-turbo-1106"
GPT_MODEL = "gpt-4-1106-preview"
JSON_MODEL = "gpt-4-1106-preview"

import time



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

    # if prompt:
    #     session.conversation.add_text_message("user", prompt)


    # parse completion
    process_completion(session, **input_completions_kwargs)

    # logging.info(f"Conversation (Post-Completion): {session.conversation.messages}")

    # determine if resubmit; can further specify resubmit conditions
    if session.conversation.messages[-1]["role"] == "tool":
        general_completion_request(
            session,
            **input_completions_kwargs,
        )




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


def get_tool_return(session, message):
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
        self.buffer_index = 0
        # if self.session.stream_handler_class.__name__ == "StreamlitStreamHandler":
        #     self.buffer_message = StreamlitMessage("assistant")
        self.buffer_message = Message("assistant", show=False)
        # elif self.session.stream_handler_class.__name__ == "PrintStreamHandler":
        #     self.buffer_message = Message("assistant")
        # self.buffer_message = Message("assistant")
        # self.streamlit_buffer_message = StreamlitMessage("assistant")

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
            self.stream_buffer(i)

        # process leftover buffer
        for i in range(-self.buffer_index, 0):
            self.stream_buffer(i)

        logging.info(f"buffer length: {len(self.buffer_message.content)}")
        logging.info(f"length of raw chunks: {len(self.raw_chunks)}")

        # finish and add message to the conversation
        self.message.finish()

        # message = general_recombine(self.raw_chunks)
        
        self.session.conversation.add_obj_message(self.buffer_message)
        logging.info(f"process_assistant_chunks: {self.session.conversation.messages[-1]}")
        # logging.info(f"text message: {self.message.api_message()}")

    def process_tool_chunks(self):
        for i, chunk in enumerate(self.completion_generator):
            i += 1  # since first chunk is already processed
            self.raw_chunks.append(chunk)

        t_response = general_recombine(self.raw_chunks)
        self.session.conversation.add_tool_response(t_response)  # make different func
        logging.info(f"process_tool_chunks: {self.session.conversation.messages[-1]}")

        t_return = get_tool_return(self.session, t_response)
        self.session.conversation.add_tool_return(t_return)
        logging.info(f"process_tool_chunks: {self.session.conversation.messages[-1]}")


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
        chunk_handler = ChunkHandler(session, completion, 
                                    #  delay=4
                                     delay=6
                                     )
        chunk_handler.process_chunks()

    # get completion generator
    completion_generator = prepare_completion_generator(
        session, **input_completions_kwargs
    )
    # now parse the stream
    parse_stream(session, completion_generator)





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