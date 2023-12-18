from datetime import datetime, timedelta
from pathlib import Path

def convert_datetime(date, time):
    # Assuming 'date' is a string in the format 'YYYY-MM-DD'
    # date_object = datetime.strptime(date, '%Y-%m-%d')
    # return date_object.strftime('%Y-%m-%d') + 'T' + time
    return datetime.strptime(date + 'T' + time + 'Z', '%Y-%m-%dT%H:%M:%SZ')

# Function to calculate the end date from start time and duration
def calculate_end_time(start_time, duration):
    # print(duration)
    hrs = duration.get('hours', 0)
    mins = duration.get('minutes', 0)
    secs = duration.get('seconds', 0)
    # print(hrs, mins, secs)
    diff = timedelta(hours=hrs, minutes=mins, seconds=secs)
    # print(start_time, diff)
    return start_time + diff

def extract_date(file_path):
    # Extract the date part from the file path
    date_str = Path(file_path).stem.split('.')[0]
    return datetime.strptime(date_str, '%Y-%m-%d')
