## for converting date info in outlook events

from pymongo import MongoClient
from dateutil.parser import parse
import json
from utils.server import HOST, PORT

# Path to your JSON file
file_path = 'examples/outlook_example.json'

# Reading the JSON data from the file
with open(file_path, 'r') as file:
    event_data = json.load(file)

# Convert date strings to datetime objects
event_data['start']['dateTime'] = parse(event_data['start']['dateTime'])
event_data['end']['dateTime'] = parse(event_data['end']['dateTime'])

client = MongoClient(HOST, PORT)
db = client['CerebraDB']
collection = db['CalendarEvents']

collection.insert_one(event_data)