from utils.sampling import select_random_members_as_dict

from server import connect_to_collection


# work in progress
def get_data(section=None, profile="llm_v1"):
    profiles = connect_to_collection()
    search = {}
    if section:
        search[section] = 1
    profile = profiles.find_one(
        {"_id": profile},
        search,
    )
    return profile


def get_elements(profile="llm_v1"):
    data = get_data("elements", profile=profile)
    return data.get("elements", {})


def get_events(profile="llm_v1"):
    data = get_data("events", profile=profile)
    return data.get("events", [])



def get_embeddings(model="text-embedding-3-small", profile="llm_v1"):
    section = "embeddings" + "." + model
    data = get_data(section, profile=profile)
    return data.get("embeddings", {}).get(model, {})


def get_data_source(source, profile="llm_v1"):
    collection = connect_to_collection()
    cursor = collection.find({"profile_id": profile, "source": source})

    items = list(cursor)
    if len(items) == 0:
        print("No items found")
    elif len(items) > 1:
        raise ValueError("More than one item found")
    else:
        items = items[0]["data"]
        if source == "events":
            # check that find retrieves single list of events
            # check ids are valid
            for event in items:
                if "id" not in event:
                    print(event)
                    raise ValueError("No id found")
                if "category" not in event:
                    print(event)
                    raise ValueError("No category found")
        if source == "keystrings":
            if not isinstance(items, list):
                raise ValueError("Keystrings is not a list")

    return items


def get_all_events_by_cat(profile="llm_v1"):
    from collections import defaultdict

    events = get_data_source("events", profile=profile)

    categories = defaultdict(list)
    for event in events:
        category = event["category"]
        categories[category].append(event)
    return categories


def get_names_by_cat(name_limit=None, profile="llm_v1"):
    events_by_cat = get_all_events_by_cat(profile=profile)

    names = {}
    for cat, events in events_by_cat.items():
        names[cat] = {}

        for event in events:
            if event["name"] not in names[cat]:
                names[cat][event["name"]] = {
                    "description": event.get("description", None)
                }

            # get ingredients
            if intake := event.get("intake"):
                for ingredient in intake["ingredients"]:
                    if "ingredients" not in names:
                        names["ingredients"] = {}
                    else:
                        if ingredient["name"] not in names["ingredients"]:
                            names["ingredients"][ingredient["name"]] = {
                                "description": ingredient.get("description", None)
                            }

            # get value names
            if values := event.get("values"):
                for value in values:
                    if cat == "meals":
                        value_string = f"{value['name']} (meal)"
                    else:
                        value_string = f"{value['name']} ({event['name']})"
                    if "values" not in names:
                        names["values"] = {}
                    if value_string not in names["values"]:
                        names["values"][value_string] = {
                            "description": value.get("description", None)
                        }

            # get people names
            if people := event.get("people"):
                for person in people:
                    person_string = f"{person['name']} ({person['role']})"
                if "people" not in names:
                    names["people"] = {}
                if person["name"] not in names["people"]:
                    names["people"][person_string] = {
                        "description": person.get("description", None)
                    }

    names["ingredients"] = names.pop("ingredients")
    names = {
        cat: {name: names[cat][name] for name in sorted(cat_names.keys())}
        for cat, cat_names in names.items()
    }

    if name_limit:
        for cat, cat_names in names.items():
            if len(cat_names) > name_limit:
                names[cat] = select_random_members_as_dict(
                    cat_names, num_members=name_limit
                )

    return names
