import pandas as pd
import json
import os
from utils.dates import convert_datetime
from utils.load import load_csv_file, load_yaml_file, load_json_template




def find_event_by_id(event_id, calendar_events):
    """
    Find an event in the calendar events list by its id.

    Args:
    event_id (str): The id of the event to find.
    calendar_events (list): List of calendar event dictionaries.

    Returns:
    dict: The found event dictionary or None if not found.
    """
    for event in calendar_events:
        if event['id'] == event_id:
            return event
    return None

def create_hobby_json(event, event_info, template, timezone):
    """
    Create a calendar event JSON from an event dictionary.
    """
    event_json = template.copy()
    event_json['name'] = event_info['name']
    event_json["type"] = event_info['type']
    event_json["enjoyed"] = event_info['enjoyed']
    event_json['start']['dateTime'] = convert_datetime(event['date'], event['start_time'])
    event_json['end']['dateTime'] = convert_datetime(event['date'], event['end_time'])    
    event_json['start']['timeZone'] = timezone
    event_json['end']['timeZone'] = timezone
    event_json['isAllDay'] = event_info['isAllDay']
    return event_json

def create_sensation_json(event, event_info, template, timezone):
    """
    Create a calendar event JSON from an event dictionary.
    """
    event_json = template.copy()
    event_json['name'] = event_info['name']
    event_json["type"] = event_info['type']
    event_json["part"] = event_info['part']
    event_json["status"]["pain"] = event_info["status"]["pain"]
    event_json['start']['dateTime'] = convert_datetime(event['date'], event['start_time'])
    event_json['end']['dateTime'] = convert_datetime(event['date'], event['end_time']) # event_json['start']['timeZone'] = timezone
    event_json['start']['timeZone'] = timezone
    event_json['end']['timeZone'] = timezone
    event_json['isAllDay'] = event_info['isAllDay']
    return event_json

def create_events(simulated_events, timezone, category, template, events_info):
    """
    Create a list of hobby event JSONs from simulated events.
    Event_info contains a list of defaults (for now, until labels can be extracted)
    """

    events_jsons = []
    for _, event in simulated_events.iterrows():
        if event['category'] == category:
            # find the event info; can change this process later
            event_info = events_info[event['id']]
            if category == 'hobbies':
                event_json = create_hobby_json(event, event_info, template, timezone)
            if category == 'sensations':
                event_json = create_sensation_json(event, event_info, template, timezone)
            events_jsons.append(event_json)

    return events_jsons

def save_to_directory(events_jsons, filename):
    """
    Save a list of JSONs to a specified directory.

    Args:
    events_jsons (list): List of calendar event JSONs.
    directory_name (str): Name of the directory to save files.
    """
    parent_dir = os.path.dirname(os.getcwd())
    save_path = os.path.join(parent_dir,f'data/sim/outputs/{filename}')
    with open(save_path, 'w') as file:
        json.dump(events_jsons, file, indent=4)


# hardcode videogames/elbow pain


parent_dir = os.path.dirname(os.getcwd())
# Load files
simulated_events = load_csv_file(os.path.join(parent_dir, 'data/sim/outputs/simulated_events.csv'))
timezone = load_yaml_file(os.path.join(parent_dir, 'data/sim/inputs/sim_params.yaml'))['timezone'] # not being appplied for now
hobby_template = load_json_template(os.path.join(parent_dir, 'data/sim/templates/hobby.json'))
sensation_template = load_json_template(os.path.join(parent_dir, 'data/sim/templates/sensation.json'))

# this is used to create event data since I haven't made label extraction script yet
hobby_event_info = load_json_template(os.path.join(parent_dir, 'data/sim/defaults/hobbies_playing_videogames.json.json'))
sensations_event_info = load_json_template(os.path.join(parent_dir, 'data/sim/defaults/sensations_elbow_pain.json'))

# Re-create calendar events with the corrected function
hobby_events_jsons = create_events(simulated_events, timezone, 'hobby', hobby_template, hobby_event_info)
# Save to directory
save_to_directory(hobby_events_jsons, "hobby_events.json")

# Re-create calendar events with the corrected function
sensation_events_jsons = create_events(simulated_events, timezone, 'sensations', sensation_template, sensations_event_info)
# Save to directory
save_to_directory(sensation_events_jsons, "sensation_events.json")

