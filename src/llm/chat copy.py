import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import json

from utils.logging_setup import set_logger
from utils.general import get_value
from viz.plot import plot_occurrence
from server.query import get_n_occurrences
from llm.my_tools.orig_tools import tools, call_function_v2
import prompts.engine as PROMPTS
from pathlib import Path
# import logging


GPT_MODEL = "gpt-3.5-turbo-0613"
# GPT_MODEL = "gpt-4"
EMBEDDING_MODEL = "text-embedding-ada-002"

# set up logs
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / f"{Path(__file__).stem}.log"
logger = set_logger(log_path)


# ChatCompletionMessage(content=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_XlPmnL6PdGd9B3v7raqWqgXS', function=Function(arguments='{\n"variable": "Basketball Game"\n}', name='get_occurrence'), type='function')]),


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(
    conversation,
    tools=None,
    tool_choice=None,
    model=GPT_MODEL,
    stream=True,
    resubmit=True,
    append=True,
):
    logger.info("Generating ChatCompletion response")

    compl_input = {
        "model": model,
        "messages": conversation.messages,
        "tools": tools,
        "tool_choice": tool_choice,
        "stream": stream,
    }
    logger.info(f"COMPL_INPUT: {compl_input}")
    try:
        client = OpenAI()
        logger.info("Calling OpenAI API")
        response = client.chat.completions.create(
            **compl_input,
        )
        # response = client.chat.completions.create(
        #                 model=model,
        #                 messages=conversation.messages,
        #                 stream=stream,
        #                 tools=tools,
        #                 tool_choice=tool_choice,
        #             )
        logger.info("COMPL_OUTPUT: {response}")
        logger.info("Received response from OpenAI API")
        if stream:
            logger.info("Processing stream response")
            chunks = [r for r in response]
            finish_reason, full_message = recombine_chunks(chunks)
            response = chunks
        else:
            logger.info("Processing non-stream response")
            finish_reason = response.choices[0].finish_reason
            full_message = response.choices[0].message
        if append:
            # logger.info(f"Stream: {response}")
            logger.info(f"Appending assistant message: {full_message}")
            conversation.messages.append(full_message)

        # make tool call if necessary
        if finish_reason == "tool_calls":
            # function = full_message["tool_calls"][0]["function"]
            tool_call = get_value(full_message, "tool_calls")[0]
            id = get_value(tool_call, "id")
            function = get_value(tool_call, "function")
            name = get_value(function, "name")

            arguments_string = get_value(function, "arguments")
            try:
                arguments = json.loads(arguments_string)
            except:
                raise Exception(f"Unable to parse arguments: {arguments_string}")

            content_output = call_function_v2(name, arguments)
            content = str(content_output)

            conversation.messages.append(
                {
                    "tool_call_id": id,
                    "role": "tool",
                    "name": name,
                    "content": content,
                }
            )
            if resubmit:
                logger.info(f"Resubmitting function: {name}")
                response = chat_completion_request(conversation, stream=stream)
        logger.info(f"Finish reason: {finish_reason}")
        return response

    except Exception as e:
        logger.exception("Unable to generate ChatCompletion response")
        logger.info(conversation.messages)
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def recombine_chunks(chunks, role="assistant"):
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


## working version
# @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
# def chat_completion_request(conversation, tools=None, tool_choice=None, model=GPT_MODEL, stream=True, resubmit=True, append=True):

#     logger.info("Generating ChatCompletion response")

#     try:
#         client = OpenAI()
#         response = client.chat.completions.create(
#                         model=model,
#                         messages=conversation.messages,
#                         stream=stream,
#                         tools=tools,
#                         tool_choice=tool_choice,
#                     )

#         if append:
#             logger.info(f"Stream: {response}")
#             assistant_message = response.choices[0].message
#             logger.info(f"Appending assistant message: {assistant_message}")
#             conversation.messages.append(assistant_message)

#         # make tool call if necessary
#         full_message = response.choices[0].message
#         if response.choices[0].finish_reason == "tool_calls":

#             function = full_message.tool_calls[0].function

#             function_content = call_function(function, conversation)
#             conversation.messages.append(
#                     {
#                         "tool_call_id": full_message.tool_calls[0].id,
#                         "role": "tool",
#                         "name": function.name,
#                         "content": str(function_content),
#                     }
#             )
#             if resubmit:
#                 logger.info(f"Resubmitting function: {function.name}")
#                 response = chat_completion_request(conversation)

#         return response

#     except Exception as e:
#         logger.exception("Unable to generate ChatCompletion response")
#         logger.info(conversation.messages)
#         print("Unable to generate ChatCompletion response")
#         print(f"Exception: {e}")
#         return e


class Conversation:
    def __init__(self, first_message=None):
        self.messages = []
        if first_message:
            self.add_message(*first_message)

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.messages.append(message)

    def display_conversation(self):
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
