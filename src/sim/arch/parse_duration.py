import yaml
from datetime import timedelta
import re

# Function to parse the duration string
def parse_duration(duration_str):
    match = re.match(r"(\d+)\s*hours?", duration_str)
    if match:
        hours = int(match.group(1))
        return timedelta(hours=hours)
    # Add more patterns here if needed
    return None

# Reading YAML file
with open('data.yaml', 'r') as file:
    data = yaml.safe_load(file)

# Extracting and parsing the duration
duration_str = data['event']['duration']
duration = parse_duration(duration_str)
print(duration)
