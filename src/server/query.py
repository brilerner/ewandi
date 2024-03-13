import sys
# print(sys.path)
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/cerebra_v2/src')
from server import connect_to_collection

from datetime import datetime


# how to define collection?? better to define as class?

def get_schema():

    collection = connect_to_collection()

    def add_name_to_schema(event, schema, cat):
        if 'name' not in event:
            pass
        else:
            if cat not in schema:
                schema[cat] = []
            if event['name'] not in schema[cat]:
                schema[cat].append(event['name'])
                
    schema = {}
    document = next(collection.find({})) # should only be one entry
    for cat,v in document.items():
        if type(v) == list:
            for event in v:
                add_name_to_schema(event, schema, cat)

    mapping = {}
    for k,v in schema.items():
        for v in v:
            mapping[v] = k
    mapping

    return mapping

def get_events(
    start_date=None, 
    end_date=None, 
    event_name=None, 
    # cat=None,
    # group=None, 
    profile='llm_v0', 
    print_events=False
    ):
    

    collection = connect_to_collection()

    schema = get_schema()
    if event_name in schema:
        cat = schema[event_name]
    else:
        print(f'event_name: {event_name} not found in schema')
        return []
    # conditions = [
    #                 {"$gte": ["$$event.start_datetime", start_date]},
    #                 {"$lte": ["$$event.start_datetime", end_date]},
    #             ]
    conditions = []
    if start_date:
        conditions.append({"$gte": ["$$event.start_datetime", start_date]})
    if end_date:
        conditions.append({"$lte": ["$$event.start_datetime", end_date]})
    if event_name:
        conditions.append({"$eq": ["$$event.name", event_name]})
    # if group:
        # conditions.append({"$eq": ["$$event.group", group]})

    pipeline = [
        {"$match": {"profile_id": profile}},  # Filter to the specific profile
        {"$project": {  # Project only the calendarEvents field
            cat: {
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
            for event in events.get(cat, []):
                print(event)

    return events_list[0][cat]

def get_n_occurrences(variable):
    events = get_events(event_name=variable)
    return len(events)
    # return events