import time
import random
from openai import OpenAI

import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)
# from utils.viz import get_plotly_figure
import prompts.engine as PROMPTS

from llm.chat import Conversation
# , chat_completion_request
# from tools.tools import tools, call_function

from utils.logging_setup import set_logger
from pathlib import Path

client = OpenAI()
GPT_MODEL = "gpt-3.5-turbo-1106"
# GPT_MODEL = 'gpt-4-1106-preview'
# GPT_MODEL = 'gpt-4-0613'
# set up logs
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / f"{Path(__file__).stem}.log"
logger = set_logger(log_path)


# @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(
    conversation,
    tools=None,
    tool_choice=None,
    model=GPT_MODEL,
    stream=False,
    resubmit=True,
    append=True,
    response_format=None,
):
    logger.info("Generating ChatCompletion response")

    compl_input = {
        "model": model,
        "messages": conversation.messages,
        "tools": tools,
        "tool_choice": tool_choice,
        "stream": stream,
        "response_format": {"type": response_format},
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


# sytem_message = """
# You are an application that breakdowns a query into a list of steps. You are part of a larger application that tracks a user's life data and allows them to query it.
# If there is more than one variable present, please return a JSON object where the key is the number the variable occurs in the entry, and the values is described below.
# Please use the following format for your response:
# {
#     "label": "<label_name>", // string, required
#     "category": "<category_name>", // string, required, choices=["nutrition", "sensation", "activity", "sleep", "medication", "mood"]
#     "attributes": "<attributes_list>", // list of strings, optional, default: []
#     "start_date": "<start_date>", // string, format: "YYYY-MM-DD", optional, default: null
#     "end_date": "<end_date>", // string, format: "YYYY-MM-DD", optional, default: null
#     "start_time": "<start_time>", // string, format: "HH:MM", optional, default: null
#     "end_time": "<end_time>", // string, format: "HH:MM", optional, default: null
#     "time_of_day": "<time_of_day>" // string, values: "morning", "afternoon", "evening", "night", optional, default: null
# }
# The time of day can be inferred.
# The attributes should be recorded as stated.
# If the category is not present in the given choices, please return null.
# These choices are: ["nutrition", "sensation", "activity", "sleep", "medication", "mood"]
# If the variable is not present, please return null.
# Here is an example to guide you:
#     user: Do I have a headache on the same days that I drink coffee?

#     assistant: {
#         "1": {
#             "label": "headache",
#             "category": "sensation",
#             "attributes": [],
#             "start_date": null,
#             "end_date": null,
#             "start_time": null,
#             "end_time": null,
#             "time_of_day": null
#         },
#         "2": {
#             "label": "coffee",
#             "category": "nutrition",
#             "attributes": [],
#             "start_date": null,
#             "end_date": null,
#             "start_time": null,
#             "end_time": null,
#             "time_of_day": null
#         }
#     }
# Go!
# """
# sytem_message = """
# You are an application that breakdowns a query into a list of steps. You are part of a larger application that tracks a user's life data and allows them to query it.
# If there is more than one variable present, please return a JSON object where the key is the number the variable occurs in the entry, and the values is described below.
# Please use the following format for your response:
# {
#     "label": "<label_name>", // string, required
#     "category": "<category_name>", // string, required, choices=["nutrition", "sensation", "activity", "sleep", "medication", "mood"]
#     "attributes": "<attributes_list>", // list of strings, optional, default: []
#     "start_date": "<start_date>", // string, format: "YYYY-MM-DD", optional, default: null
#     "end_date": "<end_date>", // string, format: "YYYY-MM-DD", optional, default: null
#     "start_time": "<start_time>", // string, format: "HH:MM", optional, default: null
#     "end_time": "<end_time>", // string, format: "HH:MM", optional, default: null
#     "time_of_day": "<time_of_day>" // string, values: "morning", "afternoon", "evening", "night", optional, default: null
# }
# The time of day can be inferred.
# The attributes should be recorded as stated.
# If the category is not present in the given choices, please return null.
# These choices are: ["nutrition", "sensation", "activity", "sleep", "medication", "mood"]
# If the variable is not present, please return null.
# Go!
# """

# sytem_message = """
# You are an application that breakdowns a query into a list of steps. You are part of a larger application that tracks a user's life data and allows them to query it.
# If there is more than one variable present, please return a JSON object where the key is the number the variable occurs in the entry, and the values is described below.
# Please use the following format for your response:
# {
#     "label": "<label_name>", // string, required
#     "category": "<category_name>", // string, required, choices=["nutrition", "sensation", "activity", "sleep", "medication", "mood"]
# }
# The time of day can be inferred.
# The attributes should be recorded as stated.
# If the category is not present in the given choices, please return null.
# These choices are: ["nutrition", "sensation", "activity", "sleep", "medication", "mood"]
# If the variable is not present, please return null.
# Here is an example to guide you:
#     user: Do I have a headache on the same days that I drink coffee?

#     assistant: {
#         "1": {
#             "label": "headache",
#             "category": "sensation",
#         },
#         "2": {
#             "label": "coffee",
#             "category": "nutrition",
#         }
#     }
# Go!
# """

sytem_message = """
You are an application that breakdowns a query into a list of steps. You are part of a larger application that tracks a user's life data and allows them to query it.
Please use the following format for your response, which should be a JSON object:
{'v':[[<label_name>, <start_date>, <end_date>, <start_time>, <end_time>]]}
If there is more than one label present, add a tuple to the list as shown above.
The date should be in "YYYY-MM-DD" format.
The time should be in "HH:MM" format.
The time of day can be inferred.
If something is not present, please return an empty string.
# Here is an example to guide you:
#     user: Do I have a headache on the same days that I drink coffee?
#     your response: {'v': [['coffee', '', '','','']]}
Go! Remember, structure each entry as a list and not a dictionary without keys.
"""


# sytem_message = """
# You are an application that breakdowns a query into a list of steps. You are part of a larger application that tracks a user's life data and allows them to query it.
# If there is more than one variable present, please return a JSON object where the key is "v" and the value is a list of the variable names extracted from the query.
# # Here is an example to guide you:
# #     user: Do I have a headache on the same days that I drink coffee?
# #     your response: {'v': ["headache", "coffee"]}
# """
def main():
    start = time.time()
    PROMPTS.system = sytem_message
    # Startthe conversation with a system message
    conversation = Conversation(first_message=("system", PROMPTS.system))

    # prompt = "Do I have a headache on the same days that I drink coffee?"
    prompt = "On days when I play bball at 6pm do I also eat pizza in the morning?"
    # prompt = "Do I ever use mouthwash?"
    conversation.add_message("user", prompt)
    chat_response = chat_completion_request(
        conversation, tools=None, model=GPT_MODEL, response_format="json_object"
    )
    # assistant_message = chat_response.choices[0].message
    conversation.display_conversation()
    duration = time.time() - start
    print(f"Duration: {duration}")


if __name__ == "__main__":
    main()
