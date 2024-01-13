import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

from llm import my_tools

func = getattr(my_tools, "tell_joke")
print(func)