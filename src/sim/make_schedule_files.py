import pandas as pd
from datetime import datetime
from utils.io import load_input_yaml, delete_directory_contents
from pathlib import Path


def get_event_info(category, event_id, yaml_data):
    for event in yaml_data[category]:
        if event['id'] == event_id:
            # Create a copy of the event dictionary and remove unnecessary keys
            event_info = event.copy()
            event_info.pop('days', None)    
            if category == 'sensations':
                event_info.pop('dependencies', None)
            return event_info
    return {}

def format_duration(duration):
    """Format the duration list of dictionaries into a human-readable string."""
    hours = duration.get('hours', 0)
    minutes = duration.get('minutes', 0)
    # Combine hours and minutes into a human-readable string
    if hours and minutes:
        return f'{hours} hours, {minutes} minutes'
    elif hours:
        return f'{hours} hours'
    elif minutes:
        return f'{minutes} minutes'
    return ''

def human_readable_key(key):
    """Convert a key from snake_case to Title Case."""
    return key.replace('_', ' ').title()

def create_intermediate_file(date, events, yaml_data, temp_dir):
    file_name = temp_dir / f'{date}.txt'
    with open(file_name, 'w') as file:
        # Write the date and day of the week
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = date_obj.strftime('%A')
        file.write(f'Date: {date} ({day_of_week})\n\n')

        # Write events grouped by category
        for category, event_ids in events.items():
            sorted_events = sorted(
                [get_event_info(category, event_id, yaml_data) for event_id in event_ids], 
                key=lambda e: e.get('start_time', '')
            )

            file.write(f'{human_readable_key(category)}:\n')
            for i, event in enumerate(sorted_events, start=1):
                file.write(f'  Event {i}:\n')
                for key, value in event.items():
                    if key == 'id':
                        continue  # Skip the 'id' key
                    if key == 'duration':
                        value = format_duration(value)
                    if key == 'start_time':
                        value = value[:-3]  # Remove seconds from start time
                    file.write(f'    - {human_readable_key(key)}: {value}\n')
            file.write('\n')


def process_day_events(date, df):
    day_events = df[df['date'] == date]
    events_by_category = {}

    for index, row in day_events.iterrows():
        category = row['category']
        event_id = row['id']

        # Initialize the category list if not already done
        if category not in events_by_category:
            events_by_category[category] = []

        # Add event to the category
        events_by_category[category].append(event_id)

    return events_by_category

def make_schedule_files(profile='llm_v0', overwrite=True):

 

    profile_dir = Path.cwd().parent /'data'/'sim' / 'profiles'/profile
    # Load the CSV file
    csv_file_path = profile_dir / 'outputs' / 'intermediate' / 'simulated_events.csv'
    schedule_df = pd.read_csv(csv_file_path)



    # Load the YAML files
    sim_params, calendar_events, sensations, hobbies = load_input_yaml(profile=profile)
    yaml_data = {
        'hobbies': hobbies,
        'calendar_events': calendar_events,
        'sensations': sensations
    }

    # Create a temp directory for intermediate files
    temp_dir = profile_dir / 'outputs' / 'intermediate' / 'temp_schedule_files'
    if temp_dir.exists():
        if overwrite:
            delete_directory_contents(temp_dir)
    else:
        temp_dir.mkdir(parents=True, exist_ok=True)

    schedule_df['date'] = schedule_df['start_datetime'].str[:10]
    # Re-run the main processing loop
    for date in schedule_df['date'].unique():
        events = process_day_events(date, schedule_df)
        create_intermediate_file(date, events, yaml_data, temp_dir)

if __name__ == 'main':
    make_schedule_files()