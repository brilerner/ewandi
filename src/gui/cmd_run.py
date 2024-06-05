import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src":
    src_dir = src_dir.parent
sys.path.append(str(src_dir))

# import prompts.engine as engine_prompts
from llm.chat import Session

debug = False
# debug = True
session = Session("brian", persistent_log=True, debug=debug)
# prompt = "Hi, what's your name?"
# prompt = "How often did I have a headache in the past month?"
# prompt = "How many times did I have computer programming homework?"
# prompt = "How many times did I have foot pain?"
prompt = "How many times have I played videogames?"
# prompt = "How often did I go hiking from 6am to 12pm?"
# prompt = "How often did I go hiking in the last month?"
# prompt = "What functions are you capable of performing?"
# session.completion_request(prompt)


def interactive_session():
    """Function to start an interactive session with GPT."""
    print("Starting an interactive session with GPT. Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break
        session.completion_request(user_input)
        # print("GPT:", response)


interactive_session()
