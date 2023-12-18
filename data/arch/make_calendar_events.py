import pandas as pd
import yaml
import json
import os
from utils.dates import convert_datetime

def load_yaml_file(file_path):
    """
    Load a YAML file and return its content.
    
    Args:
    file_path (str): Path to the YAML file.

    Returns:
    dict: Content of the YAML file.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def load_csv_file(file_path):
    """
    Load a CSV file and return its content.
    
    Args:
    file_path (str): Path to the CSV file.

    Returns:
    DataFrame: Content of the CSV file.
    """
    return pd.read_csv(file_path)

def load_json_template(file_path):
    """
    Load a JSON template file and return its content.
    
    Args:
    file_path (str): Path to the JSON file.

    Returns:
    dict: Content of the JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

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

def create_calendar_events(simulated_events, calendar_events, timezone, template):
    """
    Create a list of calendar event JSONs from simulated events.

    Args:
    simulated_events (DataFrame): DataFrame containing simulated events.
    calendar_events (list): List of calendar event specifications.
    timezone (str): Timezone string.
    template (dict): Template for the calendar event JSON.

    Returns:
    list: List of calendar event JSONs.
    """
    calendar_events_jsons = []
    for _, event in simulated_events.iterrows():
        if event['category'] == 'calendar_events':
            event_info = find_event_by_id(str(event['id']), calendar_events)
            if event_info:
                event_json = template.copy()
                event_json['subject'] = event_info['name']
                event_json["body"]['content'] = event_info['content']
                event_json["location"]['displayName'] = event_info['location']
                event_json['start']['dateTime'] = convert_datetime(event['date'], event['start_time'])
                event_json['end']['dateTime'] = convert_datetime(event['date'], event['end_time'])#calculate_end_time(event['start_time'], event['duration'])
                # event_json['start']['dateTime'] = event['start_time']
                # event_json['end']['dateTime'] = event['end_time']
                # event_json['start']['timeZone'] = timezone
                # event_json['end']['timeZone'] = timezone
                event_json['isAllDay'] = False
                # other properties
                event_json['name'] = event_info['name']
            

                calendar_events_jsons.append(event_json)

    return calendar_events_jsons

def save_to_directory(events_jsons):
    """
    Save a list of JSONs to a specified directory.

    Args:
    events_jsons (list): List of calendar event JSONs.
    directory_name (str): Name of the directory to save files.
    """
    filename = 'calendar_events.json'

    parent_dir = os.path.dirname(os.getcwd())
    save_path = os.path.join(parent_dir,f'data/sim/outputs/{filename}')
    with open(save_path, 'w') as file:
        json.dump(events_jsons, file, indent=4)



parent_dir = os.path.dirname(os.getcwd())
# Load files
simulated_events = load_csv_file(os.path.join(parent_dir, 'data/sim/outputs/simulated_events.csv'))
calendar_events = load_yaml_file(os.path.join(parent_dir, 'data/sim/inputs/calendar_events.yaml'))
timezone = load_yaml_file(os.path.join(parent_dir, 'data/sim/inputs/sim_params.yaml'))['timezone']
template = load_json_template(os.path.join(parent_dir, 'data/sim/templates/outlook_calendar_event.json'))


# Re-create calendar events with the corrected function
events_jsons = create_calendar_events(simulated_events, calendar_events, timezone, template)

# Save to directory
save_to_directory(events_jsons)
