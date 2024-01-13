
import prompts as pr
from llm.chat import json_request


CLASSIFY_NAME_MODEL = "gpt-3.5-turbo-0613"

def generate_groups(keystrings, descriptions=None, lower=True):

    prompt = pr.generate.groups(keystrings, descriptions=descriptions)
    groups = json_request(prompt)

    if 'groups' not in groups:
        raise ValueError('No groups found')
    if not isinstance(groups['groups'], list):
        raise ValueError('Groups is not a list')
    
    group_strings = []
    for group in groups['groups']:
        group = group.strip()
        if lower:
            group = group.lower()
        group_strings.append(group)
        
    return group_strings

def classify_name(name, group, description=None, model=CLASSIFY_NAME_MODEL):

    prompt = pr.generate.classify_name(name, group, description=description)

    group_decision = json_request(prompt, ASSIGN_GROUPS_MODEL)
                
    if 'is_in_group' not in group_decision:
        raise ValueError('is_in_group not found')
    elif not isinstance(group_decision['is_in_group'], bool):
            raise ValueError('is_in_group is not boolean')

    return group_decision['is_in_group']

def generate_nonexisting_keystrings(keystrings, n=5):

    prompt = pr.generate.nonexisting(keystrings, n=n)
    
    nonexisting = json_request(prompt)
    
    if 'items' not in nonexisting:
        raise ValueError('No items found')
    if not isinstance(nonexisting['items'], list):
        raise ValueError('Items is not a list')
    if len(nonexisting['items']) != n:
        raise ValueError('Incorrect number of items generated')
    
    return nonexisting['items']

def generate_variations(keystring, description=None, n=5):

    prompt = pr.generate.variations(keystring, description=description, n=n)
    
    variations = json_request(prompt)
    
    if 'variations' not in variations:
        raise ValueError('No variations found')
    if not isinstance(variations['variations'], list):
        raise ValueError('Variations is not a list')
    if len(variations['variations']) != n:
        raise ValueError('Incorrect number of variations generated')
    
    return variations['variations']