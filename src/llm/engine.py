
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
import json

from utils.viz import pretty_print_conversation
from viz import plot_occurrence
from server.query import get_schema, get_n_occurrences

import prompts.engine as PROMPTS

# to do
# 1. get embeddign funcs from notebook

GPT_MODEL = "gpt-3.5-turbo-0613"
# GPT_MODEL = "gpt-4"
EMBEDDING_MODEL = "text-embedding-ada-002"

# chat_response.choices[0] after tool call
# Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_JGeBCTAZqnC13FqECEpkCYuB', function=Function(arguments='{\n  "location": "Glasgow, Scotland",\n  "format": "celsius"\n}', name='get_current_weather'), type='function')]))

# chat_response.choices[0] after no tool call
# Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Sure, could you please provide me with the location?', role='assistant', function_call=None, tool_calls=None))

def chat_completion_with_function_execution(messages, tools=[None]):
    """
    This function makes a ChatCompletion API call with the option of adding tools.
    The conversation history is updated in call_function() if a tool is called.
    """
    response = chat_completion_request(messages, functions)

    
    full_message = response.json()["choices"][0]
    if full_message["finish_reason"] == "tool_calls":
        # print(f"Function generation requested, calling function")
        return call_function(messages, full_message)
    else:
        print(f"Function not required, responding to user")
        return response.json()

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):

    try:
        client = OpenAI()
        response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        # stream=True,
                        tools=tools,
                        tool_choice=tool_choice,
                    )
        return response
        
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def call_function(messages, full_message):
    # make tool call if necessary
    full_message = response.choices[0]
    if full_message.finish_reason == "tool_calls":
        # print(f"Function generation requested, calling function")
        return call_function(messages, full_message)
    else:
        # print(f"Function not required, responding to user")
        pass

def call_function(messages, full_message):
    # make tool call if necessary
    full_message = response.choices[0]
    if full_message.finish_reason == "tool_calls":
        # print(f"Function generation requested, calling function")
        return call_function(messages, full_message)
    else:
        # print(f"Function not required, responding to user")
        pass
"""
The logic:
make chat completion request
get response
append to messages
if tool call, call function
- the difference here is we want to feed it back in order to get the response after we give it the tool
maybe for now, to keep things more composable, I'll just leave the tool call as a separate thing; I can clean up later
"""


def call_function(messages, full_message):

    function_name = full_message["tool_calls"][0]["function"]["name"]

    if function_name == "plot_occurrence":
        try:
            function_arguments = json.loads(full_message["tool_calls"][0]["function"]["arguments"])
            print("Getting occurrences")
            fig, n = get_occurrence_information(function_arguments["variable"])
            # how to show fig???
        except Exception as e:
            print(parsed_output)
            print(f"Function execution failed")
            print(f"Error message: {e}")
        messages.append(
        {
            "tool_call_id": full_message["tool_calls"]['id'],
            "role": "tool",
            "name": full_message["tool_calls"][0]["function"]["name"],
            "content": n,
        }
        )
    else:
        raise Exception("Function does not exist and cannot be called")

class Conversation:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.conversation_history.append(message)

    def display_conversation(self, detailed=False):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        for message in self.conversation_history:
            print(
                colored(
                    f"{message['role']}: {message['content']}\n\n",
                    role_to_color[message["role"]],
                )
            )



def get_occurrence_information(variable):
    fig = plot_occurrence(variable)
    n = get_n_occurrences(variable)
    return fig, n


tools = [
{
        "type": "function",
        "function": {
            "name": "plot_occurrence",
            "description": "Tell the number of occurrences to the user and separately plot the occurrences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variable": {
                        "type": "string",
                        "description": "The variable to describe.",
                    },
                },
                "required": ["variable"],
            },
        }
    },
]
    

"""
Here are the tools that I want. Let's keep it simple so I can start builiding. For my first tool, I want to be able to plot the occurrence.
If

1. Get schema for database 

"""
### Conversation

# Start with a system message
system_message = PROMPTS.system
conversation = Conversation()
conversation.add_message("system", system_message)
chat_response = chat_completion_with_function_execution(
    conversation.conversation_history, functions=arxiv_functions
)
assistant_message = chat_response["choices"][0]["message"]["content"]
conversation.add_message("assistant", assistant_message)
display(Markdown(assistant_message))

# Add another user message to induce our system to use the second tool
conversation.add_message(
    "user",
    "Can you read the PPO sequence generation paper for me and give me a summary",
)
updated_response = chat_completion_with_function_execution(
    conversation.conversation_history, functions=arxiv_functions
)
display(Markdown(updated_response["choices"][0]["message"]["content"]))

##### NEXT STEPS
- update conversation to take tools to make adding new statements more easily
- do a test run!!!