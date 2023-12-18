import sys
# print(sys.path)
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra_v2/src')
from utils.server import connect_to_collection

from datetime import datetime



def get_events(start_date, end_date, cat, event_name=None, group=None, profile='llm_v0', print_events=False):
    
    collection = connect_to_collection()

    conditions = [
                    {"$gte": ["$$event.start_datetime", start_date]},
                    {"$lte": ["$$event.start_datetime", end_date]},
                ]
    if event_name:
        conditions.append({"$eq": ["$$event.name", event_name]})
    if group:
        conditions.append({"$eq": ["$$event.group", group]})

    pipeline = [
        {"$match": {"profile_id": profile}},  # Filter to the specific profile
        {"$project": {  # Project only the calendarEvents field
            "calendar_events": {
                "$filter": {  # Filter the calendarEvents array
                    "input": f"${cat}",
                    "as": "event",
                    "cond": {  # Condition to check the date range
                        "$and": conditions
                    }
                }
            }
        }}
    ]

    # Execute the aggregation pipeline
    cursor = collection.aggregate(pipeline)
    events_list = [event for event in cursor]

    if print_events:
        # Process and print the results
        for events in events_list:
            # print(events)
            print()
            for event in events.get("calendar_events", []):
                print(event)


    return events_list



# Define your date range
start_date = datetime(2023, 9, 1, 0, 0, 0)
end_date = datetime(2023, 9, 2, 0, 0, 0)
event_name = "Basketball Game"
get_events(start_date, end_date, 'calendar_events', event_name, profile='llm_v0', print_events=True)