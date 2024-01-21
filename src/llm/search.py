import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

from utils.paths import get_profile_dir
from utils.io import load_json

events_path = get_profile_dir("llm_v1") / "outputs/final/events_breakout.json"


# filter events

def reduce_events(events):
    reduced_names
    for event in events:
        if event["name"] not in reduced:
            reduced[event["name"]] = [event]
    return reduced

def filter_event(event):
    if event["dtype"] != "text":
        return True

all_events = load_json(events_path)
events = filter(filter_event, all_events)

print(len(list(events)))

