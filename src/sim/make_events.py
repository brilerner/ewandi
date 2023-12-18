from pathlib import Path
from utils.dates import convert_datetime
from utils.io import load_csv_file, load_yaml_file, load_json, save_jsons_to_directory
import random

def find_event_by_id(event_id, calendar_events):
    for event in calendar_events:
        if event['id'] == event_id:
            return event
    return None

# def create_events(simulated_events, cat_info):
def create_events(simulated_events, cat, input_info):
    """
    Create a list of hobby event JSONs from simulated events.
    Event_info contains a list of defaults (for now, until labels can be extracted)
    """

    events_json = []
    for _, event in simulated_events.iterrows():
        if event['category'] == cat:
            # find the event info; can change this process later
            event_input_info = find_event_by_id(str(event['id']), input_info)
            
            # template = cat_info['template']
            do_not_transfer = ['days', 'start_time', 'duration', 'dependencies']
            event_json = {k:v for k,v in event_input_info.items() if k not in do_not_transfer} 
            # event_json = {key: event_input_info[key] if key in event_input_info else None for key in template}
            event_json['start_datetime'] = event['start_datetime'].isoformat()
            event_json['end_datetime'] = event['end_datetime'].isoformat()

            events_json.append(event_json)

    return events_json

def make_events(simulated_events, profile='llm_v0'):

    # set up directories
    sim_dir = Path.cwd().parent /'data'/'sim'
    profile_dir = sim_dir / 'profiles'/profile
    save_dir = sim_dir / 'profiles'/profile/'outputs'/'final'

    
    for cat in ['calendar_events', 'hobbies', 'sensations']:
        # cat_info = {"cat":cat}
        # cat_info["template"] = load_json(sim_dir / 'templates' / f'{cat}.json')
        # cat_info["input_info"] = load_yaml_file(profile_dir / 'inputs' / f'{cat}.yaml')
        input_info = load_yaml_file(profile_dir / 'inputs' / f'{cat}.yaml')
        events = create_events(simulated_events, cat, input_info)
        save_jsons_to_directory(events, save_dir, f'{cat}.json')

if __name__ == '__main__':
    make_events()