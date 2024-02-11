I am building a keyword matching system, and need assistance in generating code. A keyword can be a word or phrase. Below, I will describe my plan and provide my current code. I would like you generate code for the full plan, by building off the current code using information from the described plan.
Please make code well-documented and pythonic.

--- START PLAN ----

I have a method to extract keywords from a user's input. I would then like to check and see if this keyword is semantically related to names in my database. A keyword can be related to either a name or a group, while a group can relate to 1 or more names. However, since I only have names in the database, I need to generate the groups.

The names are stored in a dictionary, where the key is a category. I would like to generate an encompassing set of groups for the names in a category. This should be performed by prompting an LLM. When the groups are generated for each category, I would like an LLM to determine if there are any duplicate groups, which I will then remove. Then, I would like to go through each name and have an LLM determine what groups it belongs to.

To account for user input of non-existing names or groups, I would like to generate 5 names and 5 groups that don't exist.

Then, since user input will vary from person to person, I would like to generate 5 variations of each name or group keyword (including non-existing that I generated) using an LLM.

When all variations are generated, I will then convert each keyword (including all names, groups, and variations thereof) into an embedding. Then, for each variant set (the name or group and its variations), for each variant in the set, I will calculate the cosine distance between it, i.e. the base, and its options (all existing non-variant names including the original name if the variant set pertains to a name)

To analyze the distances, I will perform the operations represented by this pseudocode:
for name_variations in existing_names
    for base in name_variations
        sort the options by distance from the base
        find the index and distance of the name
        calculate the group percentage: the percentage of options up to and including the name index that share the same group with the name
for group_variations in existing_groups
    for base in group_variations
        sort the options by distance from the base
        find the index and distance of the furthest group member
        calculate the group percentage: the percentage of options up to and including the index of the furthest group member that share the group

I would like to informatively plot the index, distance, and percentage information gathered from the described operations.

I will use this analysis to determine a proper threshold strategy for determining semantic relevance. When considering a base and the desired options retrieved, for each base the strategy should ideally capture:
- existing group >>  all names belonging to the group 
- existing name >> just that name
- non-existing group or name >> nothing
Metrics that I would like to use to evaluate the performance of a threshold choice are:
- the average success rate in retrieving a single name (for each name, success is binary)
- the average success rate in retrieving all members of a group 
- the average group percentage for names/groups
- for nonexisting names/groups, the average success rate in retrieving no items

Using the desired outcomes as evaluation metrics, I will algorithmically determine the optimal threshold by testing different thresholds and seeing the effect on the metrics.

--- END PLAN ----

--- START CODE ---


import sys
from pathlib import Path
p = Path(__file__).resolve()
while p.name != "src": p = p.parent
sys.path.append(str(p))

from openai import OpenAI

from sim import construct
from server.transfer import insert_profile_data
from server import connect_to_collection
from llm.embeddings import request_embedding, get_distance
from llm.chat import json_request
MODEL = 'gpt-4-1106-preview'

client = OpenAI()

### Get all events
    
def get_all_events(profile='llm_v1'):
    collection = connect_to_collection()
    cursor = collection.find({'profile_id':profile})
    events = list(cursor)

    # check that find retrieves single list of events
    if len(events) == 0:
        print('No events found')
    elif len(events) > 1:
        raise ValueError('More than one event found')
    events = events[0]['data']

    # check ids are valid
    for event in events:
        if 'id' not in event:
            print(event)
            raise ValueError('No id found')
        if 'category' not in event:
            print(event)
            raise ValueError('No category found')
    
    return events
        
def get_all_events_by_cat(profile='llm_v1'):
    from collections import defaultdict

    events = get_all_events(profile=profile)

    categories = defaultdict(list)
    for event in events:
        category = event['category']
        categories[category].append(event)
    return categories


def construct_strategy(profile='llm_v1'):
    
    # transfer from the database
    events_by_cat = get_all_events_by_cat(profile=profile)

    # group events
    true_event_cats = ['scheduled', 'unscheduled', 'meals', 'sleep']
    for cat, events in events_by_cat.items():
        if cat in true_event_cats:
            events_by_cat['true_event'].extend(events)
            events_by_cat.pop(cat)

    # remove categories
    skip_cats = ['scores'] # not needed, since not really an event
    for cat in skip_cats:
        events_by_cat.pop(cat)

    # get group names
    grouper_prompt = """I am going to give you an input set of words/phrases, for which I would like you to generate a a set of group names that sufficiently capture the relationships between different members of the input set.     
Any words/phrases parentheses are there to add useful context.
Please return the group names as a JSON, i.e. {'groups': ['group1', 'group2', 'group3', '...']}. 
Here is the input set:\n
"""

    no_group_cats = ['values']
    for cat, events in events_by_cat.items():
        if cat in no_group_cats:
            cat['groups'] = []
        else:
            names = [event['name'] for event in events]
            prompt = grouper_prompt.copy() + ', '.join(names)
            request_output = json_request(prompt)
            if 'groups' not in request_output:
                raise ValueError('No groups found')
            cat['groups'] = request_output['groups']
            #### finish writing code

if __name__ == '__main__':
    construct_strategy(profile='llm_v1')

--- END CODE ---

Since there are many steps here, please create code that keeps track of the information flow in an intelligble and organized way. Please make the code modular such that is easy to debug. Go!

