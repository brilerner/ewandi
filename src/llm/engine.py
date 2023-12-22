

import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')

from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import json

from utils.logging import set_logger
from utils.viz import pretty_print_conversation
from viz.plot import plot_occurrence
from server.query import get_n_occurrences
from tools.tools import tools
import prompts.engine as PROMPTS
from pathlib import Path_


# to do
# 1. get embeddign funcs from notebook

GPT_MODEL = "gpt-3.5-turbo-0613"
# GPT_MODEL = "gpt-4"
EMBEDDING_MODEL = "text-embedding-ada-002"

# chat_response.choices[0] after tool call
# Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_JGeBCTAZqnC13FqECEpkCYuB', function=Function(arguments='{\n  "location": "Glasgow, Scotland",\n  "format": "celsius"\n}', name='get_current_weather'), type='function')]))

# chat_response.choices[0] after no tool call
# Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Sure, could you please provide me with the location?', role='assistant', function_call=None, tool_calls=None))

# set up logs
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / f"{Path(__file__).stem}.log"
logger = set_logger(log_path)

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(conversation, tools=None, tool_choice=None, model=GPT_MODEL, resubmit=True, append=True):

    logger.info("Generating ChatCompletion response")

    try:
        client = OpenAI()
        response = client.chat.completions.create(
                        model=model,
                        messages=conversation.messages,
                        # stream=True,
                        tools=tools,
                        tool_choice=tool_choice,
                    )

        if append:
            assistant_message = response.choices[0].message
            logger.info(f"Appending assistant message: {assistant_message}")
            conversation.messages.append(assistant_message)

        # make tool call if necessary
        full_message = response.choices[0].message
        if response.choices[0].finish_reason == "tool_calls":

            function = full_message.tool_calls[0].function
                        
            function_content = call_function(function, conversation)
            conversation.messages.append(
                    {
                        "tool_call_id": full_message.tool_calls[0].id,
                        "role": "tool",
                        "name": function.name,
                        "content": str(function_content),
                    }
            )
            if resubmit:
                logger.info(f"Resubmitting function: {function.name}")
                response = chat_completion_request(conversation)

        return response
        
    except Exception as e:
        logger.exception("Unable to generate ChatCompletion response")
        logger.info(conversation.messages)
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def call_function(function, conversation):
    logger.info(f"Function call: {function.name}")

    if function.name == "get_occurrence":
        try:
            fargs = json.loads(function.arguments)
            n = get_n_occurrences(**fargs)
            # fig, n = get_occurrence_information(**function_arguments)
            return n # how to show fig???
        
        except Exception as e:
            logger.exception(f"Function {function.name} execution failed")
            print(f"Function execution failed")
            print(f"Error message: {e}")
    else:
        logger.exception(f"Function {function.name} does not exist and cannot be called")
        raise Exception("Function does not exist and cannot be called")

def get_occurrence_information(variable):
    logger.info(f"Running get_occurrence_information for argument: {variable}")
    # fig = plot_occurrence(variable)
    n = get_n_occurrences(variable)
    return n


class Conversation:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        logger.info(f"Adding message to conversation: {role}: {content}")
        message = {"role": role, "content": content}
        # message = {"role": role, "content": content}
        self.messages.append(message)

    def append_message(self, obj):
        self.messages.append(obj)

    def display_conversation(self, detailed=False):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        for message in self.messages:
            print(
                colored(
                    f"{message['role']}: {message['content']}\n\n",
                    role_to_color[message["role"]],
                )
            )

### Conversation

questions = (i for i in PROMPTS.questions)
# Startthe conversation with a system message
conversation = Conversation()
conversation.add_message("system", PROMPTS.system)
conversation.add_message("system", PROMPTS.schema)
# Get the initial response from the user (will integrate into streamlit after testing)
prompt = next(questions)
conversation.add_message("user", prompt)
chat_response = chat_completion_request(
    conversation, tools=tools
)
# assistant_message = chat_response.choices[0].message
pretty_print_conversation(conversation.messages)
# display(Markdown(assistant_message))