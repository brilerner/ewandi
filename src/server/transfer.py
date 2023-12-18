from pathlib import Path
import json
from utils.server import connect_to_collection
from datetime import datetime


def insert_profile_data(profile='llm_v0'):

    collection = connect_to_collection()

    base_path = Path.cwd().parent /'data'/'sim'/'profiles'/profile/'outputs'/'final'
    
    # print(base_path)
    # print(base_path.exists())
    for file_path in base_path.glob('*'):
        if file_path.is_file():
            data_category = file_path.stem

            if data_category in ['hobbies', 'sensations']:
                data_category = 'extracted'

            with open(file_path, 'r') as f:
                data = json.load(f)
            if len(data) == 0:
                continue

            convert_datetime = lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S')
            for event in data:
                if 'start_datetime' in event:
                    event['start_datetime'] = convert_datetime(event['start_datetime'])
                if 'end_datetime' in event:
                    event['end_datetime'] = convert_datetime(event['end_datetime'])
                    
            # Preparing the document to be inserted
            document = {
                "profile_id": profile,
                data_category: data
            }
            # Inserting or updating the document in MongoDB

            collection.update_one({"profile_id": profile}, {"$set": document}, upsert=True)
    print("Done inserting profile data")



# if __name__ == 'main':
insert_profile_data(profile='llm_v0')
