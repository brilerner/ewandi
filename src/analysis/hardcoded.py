import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

from utils.io import load_json
from viz.plot import plot_events, plot_numerical
from datetime import datetime
import copy


def get_all_events():
    def format_datetime(event):
        event["start_datetime"] = datetime.strptime(
            event["start_datetime"], "%Y-%m-%dT%H:%M"
        )
        event["end_datetime"] = datetime.strptime(
            event["end_datetime"], "%Y-%m-%dT%H:%M"
        )
        return event

    all_events_path = "/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/data/sim/profiles/llm_v1/outputs/final/events_breakout.json"
    all_events = load_json(all_events_path)
    all_events = [format_datetime(event) for event in all_events]
    return all_events


def filter_by_person(events, person):
    filtered_events = []
    for event in events:
        for p in event.get("people", []):
            if p["name"] == person:
                filtered_events.append(event)
                break
    return filtered_events


def get_events(name, all_events, is_value=False, person=None):
    events = []
    for event in all_events:
        if is_value and not event.get("is_value"):
            continue
        if event["name"] == name:
            events.append(event)
    if person:
        events = filter_by_person(events, person)
    return events


def get_average_score(events):
    average = 0
    for event in events:
        if not event.get("is_value"):
            continue
        try:
            average += event["value"]
        except:
            print(event)
            raise
    average = average / len(events)
    return average


def get_dates(events):
    dates = []
    for event in events:
        dates.append(event["start_datetime"])
    return dates


def person_effect_on_mood_plot(person):
    all_events = get_all_events()
    mood_events = get_events("mood", all_events, is_value=True)
    ty_dates = [d.date() for d in get_dates(filter_by_person(all_events, person))]
    mood_ty = [
        event for event in mood_events if event["start_datetime"].date() in ty_dates
    ]

    mood_events = copy.deepcopy(mood_events)
    for event in mood_events:
        event["name"] = "All Days"

    mood_ty = copy.deepcopy(mood_ty)
    for event in mood_ty:
        event["name"] = person

    fig = plot_numerical(mood_events + mood_ty)
    return fig
