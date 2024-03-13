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
prompt = "How many times did I have foot pain?"
session.completion_request(prompt)
