import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(root_path)


import logging
from llm.chat import Session


def cerebra_test_run(userid=None):
    session = Session(userid=userid)

    prompt = "What is your name?"
    # prompt = "Please tell me a joke about a janitor."
    prompt = "What is my average sleep?"

    # run request
    logging.info("SESSION STARTING")
    session.completion_request(prompt)


if __name__ == "__main__":
    """
    to
    Integrate with streamlit in simple app
    """

    cerebra_test_run(userid="brian")
