import sys
from pathlib import Path
src_dir = Path(__file__).resolve()
while src_dir.name != 'src':
    src_dir = src_dir.parent
sys.path.append(str(src_dir))

from server.transfer import upsert_data
from server.retrieve import get_elements, get_events, get_embeddings
from llm.embeddings import request_embedding


def run_maintenance(profile="llm_v1"):
    # first, update the eids for events and elements
    update_eids(profile=profile)

    # update stored name
    update_embeddings(profile=profile)


def update_eids(profile="llm_v1"):
    """Adds a unique id to each event and person in the profile. It checks if the event already exists in the elements and if so, it uses the existing eid. If not, it creates a new eid and adds it to the event and the elements.
    In elements, there are two sections: events and relations. Events are the events and relations are the people. The eid is added to the event and the person.
    In each of those sections, there is a subsection called core. This is where the elements are added. Groups are added to the groups section.

    Arguments:
        profile -- profile used to update the eids

    Returns:
        None
    """
    from utils.general import generate_uid

    event_keys = [
        "name",
        "description",
        "unit",
        "dtype",
        "category",
        "source",
        "parent_name",
    ]

    relation_keys = ["name", "description", "category"]

    def check_element_match(event, element, keep_keys):
        # print(event.keys())
        # print(element.keys())
        for k in keep_keys:
            if event.get(k) != element.get(k):
                return False
        return True  # passed all tests

    def add_elements(event, elements):
        def update_event(event, elements, section, keys):
            matching_element = None
            # check variables
            if section not in elements:
                elements[section] = {"core": {}}
            section_elements = elements[section]["core"]

            for eid, element in section_elements.items():
                if check_element_match(event, element, keys):
                    matching_element = True
                    break
            if matching_element:
                event["eid"] = eid
            else:
                event["eid"] = str(generate_uid())[:8]
                section_elements[event["eid"]] = {
                    k: v for k, v in event.items() if k in keys
                }

        update_event(event, elements, "events", event_keys)
        for person in event.get("people", []):
            update_event(person, elements, "relations", relation_keys)

    print("Updating eids")
    events = get_events(profile=profile)
    elements = get_elements(profile=profile)
    # go through each event and see if it exists in the elements
    for event in events:
        if "evid" not in event:
            event["evid"] = str(generate_uid())[:8]
        if "eid" in event:
            continue
        else:
            add_elements(event, elements)

    # upsert data
    upsert_data(events, "events", profile=profile)
    upsert_data(elements, "elements", profile=profile)


def make_stored_name(element):
    def format_value_element(element):
        return "{name} ({parent_name})".format(
            name=element["name"], parent_name=element["parent_name"]
        )

    def format_general_element(element):
        stored_name = "{name} ({category})".format(
            name=element["name"], category=element["category"]
        )
        if element.get("parent_name"):
            stored_name += " ({parent_name})".format(parent_name=element["parent_name"])
        return stored_name

    if element.get("value"):
        return format_value_element(element)
    else:
        return format_general_element(element)


def update_embeddings(model="text-embedding-3-small", profile="llm_v1"):
    def create_embedding_listing(base, text, partition, eid, element):
        return {
            "eid": eid,
            "base": base,
            "text": text,
            "partition": partition,
            "embedding": request_embedding(text, model=model),
        }

    def update_core(eid, element, element_type, partition, embeddings):
        def check_core_match(eid, embedding):
            if eid == embedding["eid"]:
                return True

        match = None
        for embedding in embeddings[element_type]:
            if check_core_match(eid, embedding):
                match = True
                break
        if not match:
            text = make_stored_name(element)
            embeddings[element_type].append(
                create_embedding_listing(text, text, partition, eid, element)
            )

    def update_name_variants(element, element_type, partition, embeddings):
        pass

        # use above code
        # generate variant, then embed
        # then onto next variant

    def update_groups(element, element_type, partition, embeddings):
        pass

    def update_group_variants(element, element_type, partition, embeddings):
        pass

    print("Updating embeddings")

    # get all the elements
    elements = get_elements(profile=profile)

    # get embeddings
    embeddings = get_embeddings(model=model, profile=profile)

    for element_type in elements.keys():  # events, relations
        for partition in elements[element_type].keys():  # core, groups
            for eid, element in elements[element_type][partition].items():
                # print(element)
                if element_type not in embeddings:
                    embeddings[element_type] = []
                update_core(eid, element, element_type, partition, embeddings)
                # update_name_variants(element, element_type, partition, embeddings)
                # update_groups(element, element_type, partition, embeddings)
                # update_group_variants(element, element_type, partition, embeddings)

    # upsert data
    upsert_data(embeddings, f"embeddings.{model}", profile=profile)


def test_run_maintenance(profile="llm_v1"):
    run_maintenance(profile=profile)
    # now look at the length of embeddings
    # embeddings = get_embeddings(profile=profile)
    # print(len(embeddings["events"]))

if __name__ == "__main__":
    run_maintenance()
    print("Done")