# First, let's load the content of the YAML files to understand their structure and contents
import pandas as pd
import datetime
from random import random # random float between 0 and 1
from utils.io import load_input_yaml
from utils.dates import convert_datetime, calculate_end_time
from pathlib import Path


# Function to parse days into a standardized format
def parse_days(days):
    if isinstance(days, list):
        return days
    else:
        return [days]

# Function to check if an event occurs on a given day
def event_occurs_on_day(event, date):
    if 'days' in event:
        event_days = parse_days(event['days'])
        if date.strftime('%a') in event_days:
            return True
    return False

# Function to add event to the daily schedule
def add_event_to_schedule(schedule, date, event, category):
    # if category == 'sensations':
    #     print(date)
    #     print(event)
    #     print()
    
    if event_occurs_on_day(event, date) or 'dependencies' in event:
        start_datetime = convert_datetime(date.strftime('%Y-%m-%d'), event['start_time'])
        event_data = {
            'category': category,
            'id': event['id'],
            'start_datetime': start_datetime,
            'end_datetime': calculate_end_time(start_datetime, event['duration'])
        }
        schedule.append(event_data)

# Function to handle dependencies from sensations.yaml
def handle_dependencies(schedule, date, event, category):
    if 'dependencies' in event:
        for dependency in event['dependencies']:
            for scheduled_event in schedule:
                if scheduled_event['id'] == dependency['id'] and random() < dependency['occurrence_prob']:
                    # print(category)
                    add_event_to_schedule(schedule, date, event, category)


def construct_schedule(profile='llm_v0'):

    sim_params, calendar_events, sensations, hobbies = load_input_yaml(profile=profile)
    # Extract start and end dates from sim_params
    start_date = datetime.datetime.strptime(sim_params['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(sim_params['end_date'], '%Y-%m-%d')

    # Initialize an empty schedule
    total_schedule = []

    # Generate schedule for each day within the date range
    current_date = start_date
    while current_date <= end_date:

        schedule = []

        # Add calendar events
        for event in calendar_events:
            add_event_to_schedule(schedule, current_date, event, 'calendar_events')

        # Add hobbies
        for hobby in hobbies:
            add_event_to_schedule(schedule, current_date, hobby, 'hobbies')

        # Check for sensations with dependencies
        for sensation in sensations:
            handle_dependencies(schedule, current_date, sensation, 'sensations')

        total_schedule.extend(schedule)
        # Move to the next day
        current_date += datetime.timedelta(days=1)

    # Convert schedule to a DataFrame
    df_schedule = pd.DataFrame(total_schedule)

    # Save the DataFrame to a CSV file
    profile_dir = Path.cwd().parent /'data'/'sim' / 'profiles'/profile
    save_dir = profile_dir / 'outputs' / 'intermediate'
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
    csv_path = save_dir / 'simulated_events.csv'
    df_schedule.to_csv(csv_path, index=False)
    return df_schedule

if __name__ == '__main__':
    construct_schedule()