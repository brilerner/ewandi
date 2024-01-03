import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')
from datetime import datetime, timedelta
from pathlib import Path
from utils.io import load_yaml_file
from utils.general import to_snake_case
import pandas as pd
import itertools
from random import random

def get_specs():
    
    profile = 'llm_v1'

    inputs_dir = Path.cwd().parent.parent /'data'/'sim' / 'profiles'/profile/'inputs'


    specs = []
    by_cat = {}
    for p in inputs_dir.glob("*.yaml"):
        if 'sim_params' in p.name:
            continue

        cat = p.stem
        cat_events = load_yaml_file(p)

        by_cat[cat] = cat_events.copy()
        
        for event_info in cat_events:
            event_info["category"] = cat
            if 'calendar' in cat:
                event_info["scheduled"] = True
            specs.append(event_info)
    return specs

# Function to parse days into a standardized format
def enforce_list(_):
    if isinstance(_, list):
        return _
    else:
        return [_]
    
def convert_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except:
        print(date_string)
        raise

def convert_start_time(time_string):
    t = timedelta()
    parts = (p for p in ['hours','minutes','seconds'])
    for p in time_string.split(":"):
        t += timedelta(**{next(parts):float(p)})
    return t
    

def convert_end_time(duration, start_time):
    return start_time + timedelta(**duration)

def check_day(spec, date):

    check_counter = 0

    # check if the event occurs within the correct date range
    if date<spec['start_date'] or date>spec['end_date']:
        check_counter += 1

    # check if event occurs on the specified day
    if days := spec.get('days'):
        if not date.strftime('%a') in days:
            check_counter += 1

    if check_counter == 0:
        return True
    else:
        return False
    
def get_sorted_pairs(day_group):
    sorted_combs = []
    for group_a, group_b in itertools.combinations(day_group, 2):
        # print(group_a)
        # print(group_b)
        time_a = group_a['start_time']
        time_b = group_b['start_time']
        if time_a < time_b:
            sorted_combs.append((group_a, group_b))
        else:
            sorted_combs.append((group_b, group_a))

    # now sort by precision
    # this can happen later if I want
    return sorted_combs

    

# get the specs for scheduled events

specs = get_specs()

# set up date range for sim
sim_params_path = "/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/Cerebra/data/sim/profiles/llm_v1/inputs/sim_params.yaml"
sim_params = load_yaml_file(sim_params_path)
default_start_date = "2022-09-01"
default_end_date = "2022-12-31"
sim_start_date = convert_date(sim_params.get("start_date", default_start_date))
sim_end_date = convert_date(sim_params.get("end_date", default_end_date))

# get dates
# start_date = convert_date(sim_start_date)
# end_date = convert_date(sim_end_date)
total_days = (sim_end_date - sim_start_date).days
dates = [sim_start_date+timedelta(days=i) for i in range(total_days+1)]

# define whole day 
START_DAY_TIME = "00:00:00"
WHOLE_DAY_DURATION = {"days":1}


# get scheduled events
scheduled_events = [spec for spec in specs if spec.get('scheduled')]

# check timing
for spec in scheduled_events:

    # give id
    spec['id'] = to_snake_case(spec['name'])

    # set up dates
    if not spec.get('start_date'):
        spec['start_date'] = sim_start_date
    else:
        spec['start_date'] = convert_date(spec['start_date'])

    if not spec.get('end_date'):
        spec['end_date'] = sim_end_date
    else:
        spec['end_date'] = convert_date(spec['end_date'])
    if spec['start_date']  > spec['end_date']:
        print("Start date comes before end date.")
        raise

    
    # set up times
    if spec.get('all_day'):
        # deal with conflicts
        if spec.get('start_time') or spec.get('duration'):
            if spec.get('start_time'):
                print('CONFLICT: all_day w/ start_time')
                raise Exception
            if spec.get('duration'):
                print('CONFLICT: all_day w/ duration')
                raise Exception
        # set times
        spec['start_time'] = START_DAY_TIME
        spec['duration'] = WHOLE_DAY_DURATION
    else:
        if not spec.get('start_time'):
            print("Need start time")
            print(spec)
            raise Exception
        if not spec.get('duration'):
            print("Need duration")
            raise Exception
    
    spec['start_time'] = convert_start_time(spec['start_time'])
    spec["end_time"] = convert_end_time(spec["duration"], spec["start_time"])
    spec["start_time_hrs"] = spec["start_time"].total_seconds()/60**2
    spec["end_time_hrs"] = spec["end_time"].total_seconds()/60**2



# make day groups
day_groups = []
for date in dates:
    day_group = []
    for spec in scheduled_events:
        if check_day(spec, date):
            # deal with probability
            if prob := spec.get('prob'):
                if random() > prob:
                    day_group.append(spec)
            else:
                day_group.append(spec)
    day_groups.append(day_group)


conflicts = []
for dg in day_groups: 
    day_conflicts = []
    if len(dg) < 2:
        pass
    else:
        for s1, s2 in get_sorted_pairs(dg):
            id_1 = s1['id']
            id_2 = s2['id']
            if s1["end_time"] >= s2["start_time"] >= s1["start_time"]:
                # day_conflicts.append((id_1, id_2))
                day_conflicts.append((s1, s2))
    conflicts.append(day_conflicts)


# def check_precision(s1, s2,)
# best to sort by precision
# add clause to check day_remove
removals = []

for day_conflicts in conflicts:

    day_remove = []

    for s1,s2 in day_conflicts:

        id_1 = s1['id']
        id_2 = s2['id']
        s1_prec = s1.get("precedence", 5)
        s2_prec = s2.get("precedence", 5)

        if s1_prec<0 or s2_prec<0:
            continue
        elif s1_prec == s2_prec:
            print(f"Precedence conflict:{id_1}, {id_2}")
            choose_spec = [s1, s1][round(random())]
            day_remove.append(choose_spec)
        elif s1_prec > s2_prec:
            day_remove.append(s2)
        else:
            day_remove.append(s1)
    removals.append(day_remove)
            

day_groups_final = []
for r, dg in zip(removals, day_groups):
    # print*
    r_ids = [s['id'] for s in r]
    day_group = [s for s in dg if s['id'] not in r_ids]
    day_groups_final.append(day_group)

# ad dates
# day_groups_final = []
for date, dg in zip(dates, day_groups_final):
    temp_dg = []
    for s in dg:
        temp_s = s.copy()
        temp_s['start_date'] = date
        temp_dg.append(temp_s)
        # print(date)
        # s['start_date'] = date
    day_groups_final.append(temp_dg)
    

all_events = [s for specs in day_groups_final for s in specs]
df_all = pd.DataFrame(all_events)
df_all.start_date.unique()
df_all.sort_values(['start_date', 'start_time_hrs'], inplace=True)
