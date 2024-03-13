import sys
from pathlib import Path
p = Path(__file__).resolve()
while p.name != 'src':
    p = p.parent
sys.path.append(str(p))

from llm.chat.sessions import Session, StreamlitSession
