import sys
from pathlib import Path
src_dir = Path(__file__).resolve()
while src_dir.name != 'src':
    src_dir = src_dir.parent
sys.path.append(str(src_dir))

from server.search import find_nearest
from server.retrieve import get_events, get_elements, get_embeddings
from datetime import datetime
from utils.dates import convert_time, keep_date, keep_time

def search_elements(v: str, element_type: str):

    def threshold_strategy(v, element_type):
        return {'events': 0.42, 'relations': 0.55}[element_type]
        
    threshold = threshold_strategy(v, element_type)
    embs = find_nearest(
                        v, 
                        element_type=element_type,
                        profile="llm_v1", 
                        threshold=threshold,
                        n=1,
                        )
    return embs

def validate_input(v: str, p: list, dr: str, tr: str, d: list):

    try:
        return _validate(v, p, dr, tr, d)
    except Exception as e:
        print(e)
        return []
    
def _validate(v: str, p: list, dr: str, tr: str, d: list):
    """
    Validate the input for a tool.

    Args:
        v (string): the event variable
        p (string): people associated with the event
        dr (string): date range of the event
        tr (string): time range of the event
        d (string): days associated with the event
    """

    import pandas as pd
    
    events = get_events(profile="llm_v1")
    elements = get_elements(profile="llm_v1")
    # embeddings = get_embeddings(profile="llm_v1")
    partitions = ['group']
    
    # variable
    v_embs = search_elements(v, "events")
    if len(v_embs) == 0:
        raise ValueError(f"Event {v} not found")
    else:
        v_emb = v_embs[0]
        partition = v_emb["partition"]
        v_elem = elements['events'][partition][v_emb["eid"]]
        # add the eid to the element (later just add to begin with)
        v_elem["eid"] = v_emb["eid"]

    # people
    if p is None:
        p_elems = []
    else:
        p_elems = []
        for p in p:
            p_embs = search_elements(p, "relations")
            if len(p_embs) == 0:
                raise ValueError(f"Person {p} not found")
            else:
                p_emb = p_embs[0]
                p_elem = elements['relations'][partition][p_emb["eid"]]
                # add the eid to the element (later just add to begin with)
                p_elem["eid"] = p_emb["eid"]
                p_elems.append(p_elem)

    # date range
    if dr:
        if '--' not in dr:
            raise ValueError(f"Invalid date range {dr}")
        else:
            dr_start, dr_end = dr.split('--')
            if dr_start == "":
                dr_start = None
            else:
                try:
                    dr_start = datetime.strptime(dr_start, "%Y-%m-%d")
                except:
                    raise ValueError(f"Invalid start date {dr_start}")

            if dr_end == "":
                dr_end = None
            else:
                try:
                    dr_end = datetime.strptime(dr_end, "%Y-%m-%d")
                except:
                    raise ValueError(f"Invalid end date {dr_end}")
                
    # time range
    if tr:
        if '--' not in tr:
            raise ValueError(f"Invalid time range {tr}")
        else:
            tr_start, tr_end = tr.split('--')
            if tr_start == "":
                tr_start = None
            else:
                try:
                    tr_start = convert_time(tr_start)
                except:
                    raise ValueError(f"Invalid start time {tr_start}")

            if tr_end == "":
                tr_end = None
            else:
                try:
                    tr_end = convert_time(tr_start)
                except:
                    raise ValueError(f"Invalid end time {tr_end}")

    ## days
    if d is None:
        d = []
    else:
        valid_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        if not all([x in valid_days for x in d]):
            raise ValueError(f"Invalid day {d}")


    v_events = []
    for event in events:
        # check if the eid is same
        if event["eid"] == v_elem["eid"]:
            datetime_info = {
                'start_date': keep_date(event["start_datetime"]),
                'end_date': keep_date(event["end_datetime"]),
                'start_time': keep_time(event["start_datetime"]),
                'end_time': keep_time(event["end_datetime"]),
                'day': datetime.strftime(event["start_datetime"], "%a"),
            }
            event.update(datetime_info)
            v_events.append(event)

    events_list = [v_events]
    if p:
        p_events = []
        for event in v_events:
            if 'people' not in event:
                continue
            event_p_eids = [p["eid"] for p in event["people"]]
            elem_p_eids = [p["eid"] for p in p_elems] 
            if not all(p in event_p_eids for p in elem_p_eids):
                continue
            p_events.append(event)
        if len(p_events) == 0:
            raise ValueError("No events found with the specified people")
        events_list.append(p_events)
        
    
    # now, check to see whether any events are in the date range
    if dr:
        dr_events = []
        for event in v_events:
            # use_event_dates = ['start_date', 'end_date'] # thought maybe I should keep events that end after midnight....
            # use_event_dates = ['start_date']
            # if dr_start:
            #     if all(dr_start<event[ds] for ds in use_event_dates):
            #         continue
            # if dr_end:
            #     if all(dr_end>event[ds] for ds in use_event_dates):
            #         continue

            if not dr_start<=event['start_date']<=dr_end:
                continue
            # then add the event to the list
            dr_events.append(event)
        if len(dr_events) == 0:
            raise ValueError("No events found in the date range")
        events_list.append(dr_events)
    

    # now check if the time range is in the list of time ranges
    if tr:
        tr_events = []
    
        for event in v_events:
            if tr_start:
                if tr_start > event["end_time"]:
                    continue
            if tr_end:
                if tr_end < event["start_time"]:
                    continue
            tr_events.append(event)
        if len(tr_events) == 0:
            raise ValueError("No events found in the time range")
        events_list.append(tr_events)

    # now check if the days are in the list of days
    if d:
        d_events = []
        for event in v_events:
            if event["day"] not in d:
                continue
            d_events.append(event)
        if len(d_events) == 0:
            raise ValueError("No events found on the specified days")
        events_list.append(d_events)


    # now, find the events that are common to all lists, where each event is dict
    # each event dict has an evid field to identify the event
    events_evids = [set([event['evid'] for event in events]) for events in events_list]
    # now get intersetcion of all the sets
    final_evids = set.intersection(*events_evids)
    # now get the events that are in the final_evids
    final_events = [event for event in v_events if event['evid'] in final_evids]

    return final_events
    



