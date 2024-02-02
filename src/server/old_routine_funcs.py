"""
Add the group names to the events.
Where a name does not have existing group membership, generate it.
People are a the sole current member of participants

is_event: top-level name in event info
is_value: value name in event info
is_ingredient: ingredient name in event info
"""

from llm.embeddings import request_embedding, get_distance as dist
from llm.generate import generate_groups
from utils.general import to_snake_case


from server.connect import connect_to_collection
from server.retrieve import get_data

from server.routines import update_eids

INGREDIENT_DESCRIPTION = "A food or drink item that is consumed."
INGREDIENT_CATEGORY = "dietary intake"

### Server


def replace_section(data, section, profile_id="llm_v1"):
    collection = connect_to_collection()

    # Perform the update
    collection.update_one(
        {"profile_id": profile_id, "section": section}, {"$set": {"data": data}}
    )


def add_to_array(value_to_add, section, profile_id="llm_v1"):
    """
    If it can't find the right array, nothing happens
    """
    collection = connect_to_collection()
    collection.update_one(
        {"profile_id": profile_id}, {"$push": {section: value_to_add}}
    )


def add_entry(key, value, section, profile_id="llm_v1"):
    """ """
    collection = connect_to_collection()
    collection.update_one({"profile_id": profile_id}, {"$set": {section: {key: value}}})


### formatting


def get_stored_nids(section):
    if len(section.split(".")) != 3:
        raise ValueError("Section must be of the form '90.section.core'")
    if section.split(".")[0] != "keywords":
        raise ValueError("Section must be of the form 'keywords.section.core'")

    keywords = get_data(section)
    return list(keywords.keys())


def format_nid(keystring, parent_name=None):
    """
    Parent_name signifies value
    """

    keystring = keystring.strip()
    keystring = to_snake_case(keystring)

    if parent_name:
        return to_snake_case(parent_name) + "." + keystring
    else:
        return keystring


def format_stored_name(name, parent=None):
    name = name.strip()
    if parent:
        return parent + " " + name
    else:
        return name


def format_stored_description(description):
    """
    Capitalize the first letter of the description if it isn't already.
    Add a period to the end of the description if it doesn't have one.
    """
    description = description.strip()
    if description[0].islower():
        description = description[0].upper() + description[1:]
    if description[-1] != ".":
        description += "."
    return description


def add_source(event):
    if event["category"] == "unscheduled":
        event["source"] = "extracted"


def add_nids(replace=True):
    events = get_data("elements")
    for event in events:
        if "nid" not in event or replace:
            event["nid"] = format_nid(event["name"])
        if "description" in event:
            event["description"] = format_stored_description(event["description"])
        for value in event.get("values", []):
            if "nid" not in value or replace:
                value["nid"] = format_nid(value["name"], parent=event["name"])
            if "description" in value:
                value["description"] = format_stored_description(value["description"])
        if intake := event.get("intake"):
            for ingredient in intake["ingredients"]:
                if "nid" not in ingredient or replace:
                    ingredient["nid"] = format_nid(ingredient["name"])
                if "description" not in ingredient or replace:
                    ingredient["description"] = format_stored_description(
                        INGREDIENT_DESCRIPTION
                    )
    replace_section(events, "elements")


### updates


def update_people():
    def find_people():
        events = get_data("elements")
        people = []
        for event in events:
            if event_people := event.get("people", None):
                people.extend(event_people)
        return list(set(people))

    def add_person(person):
        nid = format_nid(person["name"])
        person_data = {
            "stored_name": format_stored_name(person["name"]),
        }
        add_entry(nid, person_data, "keywords.participants.core")

    # add people information
    retrieved_people = find_people()

    existing_nids = get_stored_nids("participants.core")

    for person in retrieved_people:
        if format_nid(person) not in existing_nids:
            add_person(person)


def update_events():
    def add_event(event):
        nid = format_nid(event["name"])
        data = {
            "stored_name": format_stored_name(event["name"]),
            "category": event["category"],
            "is_event": True,
        }
        add_entry(nid, data, "keywords.elements.core")

    def add_value(value, event):
        nid = format_nid(value["name"], parent=event["name"])
        data = {
            "stored name": format_stored_name(value["name"], event["name"]),
            "is_value": True,
            "category": None,
        }
        add_entry(nid, data, "keywords.elements.core")

    def add_ingredient(ingredient, event):
        nid = format_nid(ingredient["name"])
        data = {
            "nid": ingredient["nid"],
            "stored_name": format_stored_name(ingredient["name"]),
            "category": INGREDIENT_CATEGORY,
            "is_ingredient": True,
        }
        add_entry(nid, data, "keywords.elements.core")

    def event_check(event):
        if event["category"] == "scores":
            return False
        else:
            return True

    stored_nids = get_stored_nids("elements.core")
    for event in get_data("events"):
        if event_check(event) and event["nid"] not in stored_nids:
            add_event(event)
        for value in event.get("values", []):
            if value["nid"] not in stored_nids:
                add_value(value, event)
        if intake := event.get("intake"):
            for ingredient in intake["ingredients"]:
                add_ingredient(ingredient, event)


def update_keywords():
    update_people()
    update_events()


### groups


def add_groups():
    def add_group(name, category, section):
        nid = format_nid(name)
        data = {
            "stored_name": format_stored_name(group),
            "category": category,
            "assigned": False,  # to track whether singles have been
        }
        add_entry(nid, data, "keywords.elements.groups")

    def get_kw_by_cat(event_kw):
        from collections import defaultdict

        by_cat = defaultdict(list)
        for kw in event_kw:
            if category := kw.get("category", None):
                by_cat[category].append(kw)
        by_cat = {k: list(set(v)) for k, v in by_cat.items()}
        return by_cat

    keywords = get_data("keywords")

    for section, kw_modes in keywords.items():
        by_cat = get_kw_by_cat(section["core"])
        current_groups = [g["nid"] for g in kw_modes.get("groups", [])]
        # generate groups
        for category, keywords in by_cat.items():
            if category == "groups":
                continue
            # add in descriptions?
            generated_groups = generate_groups(keywords)
            add_groups = [g for g in generated_groups if g not in current_groups]
            for group in add_groups:
                add_group(group, category, section)


def add_embeddings():
    """
    Add embeddings to every keystring.
    """

    embedded_nids = get_stored_nids(
        "embeddings.elements"
    )  # probably not optimally scalable; could check for is_embedded
    keywords = get_data("keywords")
    for section, kw_modes in keywords.items():  # events, people
        for kw_mode, kws in kw_modes.items():  # names, groups
            for kw, kw_info in kws.items():
                if kw_info["nid"] in embedded_nids:
                    continue
                else:
                    embedding_info = {
                        "nid": kw_info["nid"],
                        "embedding": kw_info["embedding"],
                    }
                    add_to_array(embedding_info, "embeddings.elements")


def match_keyword(keyword_string, threshold=0.12, section="elements"):
    input_embedding = request_embedding(keyword_string)
    embeddings = get_data(f"embeddings.{section}")
    matched_embeddings = [
        embedding
        for embedding in embeddings
        if dist(embedding["embedding"], input_embedding) < threshold
    ]
    return matched_embeddings