import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

from gui.components.calendar_tab import show_calendar
from gui.components.chatbot import show_chatbot
from gui.components.values import show_sleep, show_survey
