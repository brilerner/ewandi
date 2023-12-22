import time
import random
from openai import OpenAI

import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')
# from utils.viz import get_plotly_figure
import prompts.engine as PROMPTS

from llm.chat import Conversation 
#, chat_completion_request
from tools.tools import tools_final, call_function

from utils.logging import set_logger
from pathlib import Path

client = OpenAI()
GPT_MODEL = 'gpt-3.5-turbo-1106'
# GPT_MODEL = 'gpt-4-1106-preview'
# GPT_MODEL = 'gpt-4-0613'
# set up logs
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / f"{Path(__file__).stem}.log"
logger = set_logger(log_path)


# @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(conversation, tools=None, tool_choice=None, model=GPT_MODEL, stream=False, resubmit=True, append=True, response_format=None):

    logger.info("Generating ChatCompletion response")

    compl_input = {
        "model": model,
        "messages": conversation.messages,
        "tools": tools,
        "tool_choice": tool_choice,
        "stream": stream,
        "response_format": {"type":response_format},

    }
    logger.info(f"COMPL_INPUT: {compl_input}")
    try:
        client = OpenAI()
        logger.info("Calling OpenAI API")
        response = client.chat.completions.create(
                        **compl_input,
                    )
        
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
    



sytem_message = """
You are an application that breakdowns a query into a list of steps. You are part of a larger application that tracks a user's life data and allows them to query it.
Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
"""
PROMPTS.system = sytem_message
qs= [
    "How many times have I gone to a basketball game?"

]
questions = (i for i in qs)
tools = tools_final
def main():

    start = time.time()
    # Startthe conversation with a system message
    conversation = Conversation(first_message = ("system", PROMPTS.system))

    

    conversation.add_message("user", next(questions))

    chat_response = chat_completion_request(
        conversation, tools=tools, model=GPT_MODEL, resubmit=False
    )
    # assistant_message = chat_response.choices[0].message
    conversation.display_conversation()
    duration = time.time() - start
    print(f"Duration: {duration}")



if __name__ == "__main__":
    main()  