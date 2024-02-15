import sys
from pathlib import Path
src_dir = Path(__file__).resolve()
while src_dir.name != 'src':
    src_dir = src_dir.parent
sys.path.append(str(src_dir))

from llm.my_tools import tools
import json

print(json.dumps(tools, indent=4))