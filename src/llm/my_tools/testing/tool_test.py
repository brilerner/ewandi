import sys
from pathlib import Path
p = Path(__file__).resolve()
while p.name != 'src':
    p = p.parent
sys.path.append(str(p))

from llm.my_tools import tools
import json

print(json.dumps(tools, indent=4))