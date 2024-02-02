import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

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


# GPT_MODEL = "gpt-3.5-turbo-0613"
GPT_MODEL = "gpt-4-1106-preview"


# def main_function(self):
#     # You can access self.userid here
#     self.nested_function()

# def nested_function(self):
#     # userid is accessible here as well
#     print(f"The userid is {self.userid}")
import time


class Conversation:
    """
    First message is a system message
    """

    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.messages.append(message)

    def get_display_messages(self):
        messages_to_display = []
        for message in self.messages:
            logging.info(f"message : {message}")
            if not isinstance(message, dict):
                message = dict(message)
            if message["role"] != "system" and message["role"] != "tool":
                # logging.info(f"message : {message}")
                messages_to_display.append(message)
        return messages_to_display

    def display_conversation(self):
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


def format_tool_response(recombined_message, tool_module, userid):
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
            for tool in tool_module.tools:
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
        args = [userid] + args
        return getattr(tool_module, function_name)(*args, **kwargs)

    tool_call = get_value(recombined_message, "tool_calls")[0]
    id = get_value(tool_call, "id")
    function = get_value(tool_call, "function")
    function_name = get_value(function, "name")

    arguments_string = get_value(function, "arguments")
    arguments = json.loads(arguments_string)

    # try:
    # except:
    #     raise Exception(f"Unable to parse arguments: {arguments_string}")

    content = call_function(function_name, arguments, userid)
    # need to make into str?
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
    finish_reason = None
    for chunk in chunks:
        if chunk.choices[0].finish_reason:
            finish_reason = chunk.choices[0].finish_reason

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

    return finish_reason, msg


def remove_word_and_rechunk(chunks, word):
    # Combine chunks into a single string
    combined = "".join(chunks)

    # Remove the specified word and keep track of the indices where it was removed
    removal_indices = []
    start = 0
    while start < len(combined):
        index = combined.find(word, start)
        if index == -1:
            break
        removal_indices.extend(range(index, index + len(word)))
        start = index + 1

    # Break the modified string back into chunks
    new_chunks = []
    start = 0
    for chunk in chunks:
        new_chunk = ""
        for i in range(start, start + len(chunk)):
            if i not in removal_indices:
                new_chunk += combined[i] if i < len(combined) else ""
        new_chunks.append(new_chunk)
        start += len(chunk)

    return new_chunks


def handle_tool_stream(completion):
    for i, chunk in enumerate(completion):
        logging.info(chunk)


def handle_stream_output(content, stream_handler="print"):
    if stream_handler == "print":
        print(content, end="")
    else:
        stream_handler.markdown(content)


def handle_stream_completion(
    session,
    completion,
    placeholder=None,
    tool_module=None,
    stream_handler="print",
    plot_handler="show",
):
    """
    handle_plot enables the plot to display during streaming
    """

    def handle_plot(session, placeholder):
        fig = load_temp_plot(session, placeholder)
        if plot_handler == "show":
            fig.show()
        else:
            plot_handler(placeholder)

    current_message = ""
    delay = 4
    previous_content_chunks = []
    raw_chunks = []
    is_tool = False
    for i, chunk in enumerate(completion):
        raw_chunks.append(chunk)
        logging.info(chunk)

        # check if tool response; use first since last chunk has no tools, just finish reason = tool calls
        if i == 0:
            if chunk.choices[0].delta.tool_calls:
                is_tool = True
                continue

        # if not tool response, handle as normal
        if is_tool:
            pass  # recombine can handle all the chunks
            # if finish_reason == "stop":
            #     break

        else:
            finish_reason = chunk.choices[0].finish_reason
            if finish_reason == "stop":
                if stream_handler == "print":
                    for i in list(range(delay))[::-1]:
                        time.sleep(0.1)
                        print(previous_content_chunks[-(i + 1)], end="")
                        # handle_stream_output(
                        #     previous_content_chunks[-(i + 1)], stream_handler
                else:
                    stream_handler.markdown("".join(previous_content_chunks))
                    respond(
                        "".join(previous_content_chunks),
                        stream_handler,
                    )

# MAKE SURE MARKDOWN AND MESSAGE APPENDING ARE BEING PERFORMED CORRECTLY
                break

            content = chunk.choices[0].delta.content
            current_message += content
            previous_content_chunks.append(content)

            if i < delay:
                pass
            else:
                if placeholder and (placeholder in current_message):
                    handle_plot(session, placeholder)
                    # previous_content_chunks[0] = previous_content_chunks[0].strip()
                    previous_content_chunks = remove_word_and_rechunk(
                        previous_content_chunks, placeholder
                    )
                if stream_handler == "print":
                    print(previous_content_chunks[i - delay], end="")
                else:
                    stream_handler("".join(previous_content_chunks) + "▌")
                # handle_stream_output(message_to_display + "▌", stream_handler)
                # handle_stream_output(previous_content_chunks[i - delay], stream_handler)
    #
    finish_reason, recombined_message = general_recombine(raw_chunks)
    # append intial tool response
    session.messages.append(recombined_message)
    # session.conversation.messages.append(recombined_message)
    if finish_reason == "tool_calls":
        recombined_message = format_tool_response(
            recombined_message, tool_module, session.userid
        )
        session.messages.append(recombined_message)
    logging.info(f"RECOMBINED: {recombined_message}")
    return finish_reason, recombined_message


def run_completion(client, backoff=True, **completions_kwargs):
    if backoff:

        @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
        def completion_func():
            return client.chat.completions.create(**completions_kwargs)
    else:

        def completion_func():
            return client.chat.completions.create(**completions_kwargs)

    return completion_func()


def general_completion_request(
    session,
    tool_module=None,
    handlers=None,
    placeholder=None,
    **input_completions_kwargs,
):
    """
    Any extra kwargs will go into the api call.
    This is where the request is made; handle_steam_completion is where the response is parsed.
    The placeholder is generated when a tool response is parsed.
    The placeholder is extracted when the assistant response to the tool is parsed.
    """
    # update defaults
    completions_kwargs = {
        "model": GPT_MODEL,
        "messages": session.messages,
        # "messages": session.conversation.messages,
        "stream": True,
    }
    completions_kwargs.update(input_completions_kwargs)
    if tool_module:
        completions_kwargs["tools"] = tool_module.tools

    # logging.info(f"Conversation (Pre-Completion): {session.conversation.messages}")
    logging.info(f"Conversation (Pre-Completion): {session.messages}")

    # get completion generator
    completion = run_completion(session.client, session.backoff, **completions_kwargs)

    # parse completion
    if completions_kwargs["stream"]:
        finish_reason, recombined_message = handle_stream_completion(
            session, completion, placeholder, tool_module=tool_module, **handlers
        )
    else:
        # logging.info(completion)
        # content = completion.choices[0].message.content
        print("Non-streaming not currently supported.")
        raise NotImplementedError

    # always append
    # session.conversation.messages.append(recombined_message)
    # session.messages.append(recombined_message)

    placeholder = None  # just in case
    # determine if resubmit; can further specify resubmit conditions
    if finish_reason == "tool_calls":
        placeholder = recombined_message["content"].get("placeholder")
        recombined_message["content"] = str(recombined_message["content"])
        general_completion_request(
            session,
            tool_module,
            handlers=handlers,
            placeholder=placeholder,
            **input_completions_kwargs,
        )


def respond(prompt, stream_handler):
    full_response = ""
    for r in prompt:
        time.sleep(0.05)
        full_response += r
        stream_handler.markdown(full_response + "▌")
    stream_handler.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    return message


def cerebra_completion_request(session, stream_handler="print", plot_handler="show"):
    """
    This is where the main error handling is performed.
    This is also where I add in tools and some specificications for the run.
    """

    handlers = {"stream_handler": stream_handler, "plot_handler": plot_handler}

    try:
        # response = respond("hello", stream_handler)
        # return response
        response = general_completion_request(
            session,
            tool_module=my_tools,
            model=GPT_MODEL,
            handlers=handlers,
        )
        return response

    except Exception as e:
        err_msg_for_user = handle_error(e)
        # session.conversation.messages.append(
        #     {"role": "assistant", "content": err_msg_for_user}
        # )
        # session.messages.append({"role": "assistant", "content": err_msg_for_user})
        if isinstance(stream_handler, str) and stream_handler == "print":
            print(err_msg_for_user)
        else:
            respond(err_msg_for_user, stream_handler, session)
        return {"role": "assistant", "content": err_msg_for_user}


class CerebraUserSession:
    def __init__(self, userid=None):
        self.userid = userid
        self.add_userid_if_missing()
        self.conversation = self.start_cerebra_conversation()
        self.messages = self.conversation.messages
        self.backoff = True
        self.client = OpenAI()

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

    def start_cerebra_conversation(self):
        conversation = Conversation()
        conversation.add_message("system", engine_prompts.system)
        return conversation


def cerebra_test_run(userid=None):
    session = start_cerebra_session(userid=userid, backoff=True)

    user_prompt = "What is the average for sleep?"
    session.conversation.add_message("user", user_prompt)

    # run request
    logging.info("SESSION STARTING")
    cerebra_completion_request(session)  # **handlers)


if __name__ == "__main__":
    """
    to
    Integrate with streamlit in simple app
    """

    cerebra_test_run(userid="brian")


#### simple


def get_completion(prompt, model="gpt-4", response_format=None):
    client = OpenAI()
    messages = [{"role": "user", "content": prompt}]
    print(response_format)
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0, response_format=response_format
    )
    return response.choices[0].message.content


# system_prompt = """Prepare for two pieces of information: a description of a plot and a code for that plot. The code will be "PH-" followed by four integers. Please respond with an elaborated description of the plot. Within this description, please include the code for the plot at a place where it should ideally be shown. The code must occur in between sentences or after the period of the last sentence with no period after the code. Respond concisely.
# """

# plot_description = f"""Description: This plot shows a sine wave with noise. The x-axis is labeled "X Axis" and the y-axis is labeled "Y Axis". The title of the plot is "Simulated Data: Sine Wave with Noise"." Code: {placeholder}"""

# simple_prompt = f"""This is a test prompt. Please respond with a short sentence, followed by this string directly after the period with no space: "{placeholder}"."""

# joke_prompt = """Tell a joke about a banana."""
# fig = get_plotly_figure()
# placeholder = save_temp_plot(fig)
# conv.add_message("user", "Hello, how are you?")
# conv.add_message("system", system_prompt)
# conv.add_message("user", plot_description)
# conv.add_message("user", simple_prompt)
