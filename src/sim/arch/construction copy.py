import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')
from datetime import datetime, timedelta
from pathlib import Path
from utils.io import load_yaml_file, load_json
from utils.general import to_snake_case
import pandas as pd
import itertools
import random
import numpy as np


# keep in mind..
# - makes sure I am copying where necessary

# inputs_dir = Path.cwd().parent.parent /'data'/'sim' / 'profiles'/profile/'inputs'

profile_path = "/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/Cerebra/data/sim/profiles/llm_v1"
inputs_dir = Path(profile_path) / "inputs"
outputs_dir = Path(profile_path) / 'outputs'



# define whole day 
START_DAY_TIME = "00:00:00"
WHOLE_DAY_DURATION = {"days":1}
DEFAULT_DURATION = {"hours":1}
DEFAULT_START_DATE = "2022-09-01"
DEFAULT_END_DATE = "2022-12-31"

def run(profile = 'llm_v1'):
# set up date range for sim

    sim_params_path = inputs_dir / "sim_params.yaml"
    sim_params = load_yaml_file(sim_params_path)

    sim_start_date = convert_date(sim_params.get("start_date", DEFAULT_START_DATE))
    sim_end_date = convert_date(sim_params.get("end_date", DEFAULT_END_DATE))
    total_days = (sim_end_date - sim_start_date).days
    dates = [sim_start_date+timedelta(days=i) for i in range(total_days+1)]

    args = {'sim_start_date':sim_start_date, 'sim_end_date':sim_end_date, 'dates':dates}


    recipes_path = outputs_dir / 'intermediate' / 'recipes_final.json'
    recipes = load_json(recipes_path)


    # setup
    specs = get_specs()
    format_events(specs, args)

    # scheduled events
    day_groups_final_scheduled = determine_final_day_groups(specs['scheduled'], dates)

    # unscheduled events
    day_groups_final_unscheduled = determine_final_day_groups(specs['unscheduled'], dates)
    combined_day_groups = combine_day_groups(day_groups_final_scheduled, day_groups_final_unscheduled)
    day_groups_final = deal_with_conflicts(combined_day_groups)
        
    # add meals
    day_groups_meals = make_day_groups(specs['meals'], dates)
    add_recipes_to_meals(day_groups_meals, recipes)
    combined_day_groups_meals = combine_day_groups(day_groups_final, day_groups_meals)

    # add sensations
    day_groups_sensations = make_day_groups(specs['sensations'], dates, existing_events=combined_day_groups_meals)
    combined_day_groups = combine_day_groups(combined_day_groups_meals, day_groups_sensations)

    # add sleep
    # day_groups_sleep = make_day_groups(specs['sleep'], dates)

    # create scores
    final_groups = make_scores(combined_day_groups, 
                               score_constructor=specs['scores'],
                               people_constructor=specs['people'])

    final_groups = format_final_specs(final_groups, dates)
    df = get_full_df(final_groups)
    return df
    # display(df)
    # df.groupby('start_date').filter(lambda x: x.id.str.contains('head').any())
    # # do this at the end

def get_specs(profile = 'llm_v1'):
    
    specs = []
    by_cat = {}
    for p in inputs_dir.glob("*.yaml"):
        if 'sim_params' in p.name:
            continue

        cat = p.stem
        cat_events = load_yaml_file(p)

        
        for event_info in cat_events:
            event_info["category"] = cat
            if 'calendar' in cat:
                event_info["scheduled"] = True
            specs.append(event_info)

        by_cat[cat] = cat_events
    
        
    return by_cat

## Sec: Construct

def determine_final_day_groups(events, dates):
    day_groups = make_day_groups(events, dates)
    day_groups = deal_with_conflicts(day_groups)
    return day_groups


## Sec: Day groups

def make_day_groups(events, dates, existing_events=None):
    day_groups = []
    for i, date in enumerate(dates):

        day_group = []
        for spec in events:
            if not check_day(spec, date):
                continue
            if existing_events:
                if not 'causes' in spec:
                    continue
                if not check_causes(spec, existing_events[i]):
                    continue
            # deal with probability
            if prob := spec.get('prob'):
                if random.random() > prob:
                    day_group.append(spec)
            else:
                day_group.append(spec)
        day_groups.append(day_group)

    # format_events(day_groups)
    return day_groups

def combine_day_groups(dg1, dg2):
    combined_day_groups = []
    for d1, d2 in zip(dg1, dg2):
        combined_day_groups.append(d1+d2)
    return combined_day_groups

## Sec: Conflict resolution

def deal_with_conflicts(day_groups):
    conflicts = make_conflict_groups(day_groups)
    removals = make_removal_groups(conflicts)
    return  remove_conflicts(day_groups, removals)

def sort_precision(day_conflicts):
    def get_top_precedence(tup):
        s1, s2 = tup
        s1_precedence = s1.get("precedence", 5)
        s2_precedence = s2.get("precedence", 5)
        return min(s1_precedence, s2_precedence)

    day_conflicts.sort(key=get_top_precedence)
    return day_conflicts

def make_conflict_groups(day_groups):

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
                    # to make sorting precision easier later
                    if s1.get('precedence',5) < 0 or s2.get('precedence',5) < 0:
                        continue
                    else:
                    # day_conflicts.append((id_1, id_2))
                        day_conflicts.append((s1, s2))
        conflicts.append(day_conflicts)

    return conflicts


def make_removal_groups(conflicts):
    removals = []
    for day_conflicts in conflicts:

        day_remove = []
        day_conflicts = sort_precision(day_conflicts)

        for s1,s2 in day_conflicts:

            id_1 = s1['id']
            id_2 = s2['id']
            s1_prec = s1.get("precedence", 5)
            s2_prec = s2.get("precedence", 5)

            # check if already removed
            existing_remove_ids = [s['id'] for s in day_remove]
            if id_1 in existing_remove_ids or id_2 in existing_remove_ids:
                continue

            if s1_prec<0 or s2_prec<0:
                continue
            elif s1_prec == s2_prec:
                print(f"Precedence conflict:{id_1}, {id_2}")

                # choose conflict randomly
                remove_spec = [s1, s1][round(random.random())]
            elif s1_prec > s2_prec:
                remove_spec = s2
            else:
                remove_spec = s1
            # remove_id = remove_spec['id']
            day_remove.append(remove_spec)
        removals.append(day_remove)
    return removals

def remove_conflicts(day_groups, removals):
    day_groups_final = []
    for r, dg in zip(removals, day_groups):
        # print*
        r_ids = [s['id'] for s in r]
        day_group = [s for s in dg if s['id'] not in r_ids]
        day_groups_final.append(day_group)
    return day_groups_final

### Pre-formatting functions

def format_category(specs, args, category='scheduled'):


    process_dates = ['scheduled', 'sensations', 'unscheduled', 'scores']
    process_times = process_dates + ['meals']

    # check timing
    
    for spec in specs:

        # give id
        spec['id'] = to_snake_case(spec['name'])

        if category in process_dates:
            format_dates(spec, args)
        if category in process_times:
            format_times(spec)

        
def format_events(specs, args):

    for category, specs in specs.items():   
        format_category(specs, args, category=category)

def format_times(spec):
        

        # set up times
        if spec.get('delay'):
            if spec.get('all_day'):
                print('CONFLICT: delay w/ all_day')
                raise Exception
            if spec.get('start_time'):
                print('CONFLICT: all_day w/ start_time')
                raise Exception
            if spec.get('end_time'):
                print('CONFLICT: all_day w/ end_time')
                raise Exception
            elif not spec.get('duration'):
                spec['duration'] = DEFAULT_DURATION

            # if duration := spec.get('duration'):
            #     if mode := duration.get('mode'):
            #         if mode == 'sampled':
            #             pass

 
            # format
            spec['delay'] = timedelta(**spec['delay'])
            spec['duration'] = timedelta(**spec['duration'])
        else:
            if spec.get('all_day'):
                # deal with conflicts
                if spec.get('start_time') or spec.get('duration'):
                    if spec.get('start_time'):
                        print('CONFLICT: all_day w/ start_time')
                        raise Exception
                    if spec.get('end_time'):
                        print('CONFLICT: all_day w/ end_time')
                        raise Exception
                    if spec.get('duration'):
                        print('CONFLICT: all_day w/ duration')
                        raise Exception
                    if spec.get('delay'):
                        print('CONFLICT: all_day w/ delay')
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
            spec['duration'] = timedelta(**spec['duration'])

def format_dates(spec, args):
    # set up dates
    if not spec.get('start_date'):
        spec['start_date'] = args['sim_start_date']
    else:
        spec['start_date'] = convert_date(spec['start_date'])

    if not spec.get('end_date'):
        spec['end_date'] = args['sim_end_date']
    else:
        spec['end_date'] = convert_date(spec['end_date'])
    if spec['start_date']  > spec['end_date']:
        print("Start date comes before end date.")
        raise
        

### Timing functions

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

### Validation functions

def check_day(spec, date):

    check_counter = 0

    # check if the event occurs within the correct date range

    if 'start_date' in spec:
        if date<spec['start_date']:
            check_counter += 1
    if 'end_date' in spec:
        if date>spec['end_date']:
            check_counter += 1

    # check if event occurs on the specified day
    if days := spec.get('days'):
        if not date.strftime('%a') in days:
            check_counter += 1

    if check_counter == 0:
        return True
    else:
        return False
    

# Sec: Causes
    
def check_single_cause(cause, existing_events_for_day):

    cause_types = ['ingredient', 'standard']

    cause_type = cause.get('type', 'standard')
    if cause_type not in cause_types:
        print("cause type not recognized")
        raise Exception

    for existing_event in existing_events_for_day:
        if cause_type == 'ingredient':
            if recipe := existing_event.get('recipe'):
                ingredient_names = [i['name'] for i in recipe['ingredients']]
                if cause['name'] in ingredient_names:
                    return existing_event
        elif cause_type == 'standard':

            if existing_event['name'] == cause['name']:
                return existing_event
    return None # this means no cause was found

def check_causes(spec, existing_events_for_day):

    cause = spec['causes'][0] # not set up for multiple causes yet
    if existing_event := check_single_cause(cause, existing_events_for_day):
        if 'delay' in spec:
            spec["start_time"] = existing_event['start_time'] + spec['delay']
            spec["end_time"] = spec['start_time'] + spec['duration']
        return True
    else:
        return False
    
## Sec: Effects

    

def adjust_score(effect, current_scores):

    def sample_score(effect):
        values = effect['vals']

        if 'probs' in effect:
            probabilities = effect['probs']
        else:
            probabilities = [1/len(values) for _ in values]
            
        return np.random.choice(values, p=probabilities)
    
    # get current score for effect
    cs = [cs for cs in current_scores if cs['name'] == effect['name']][0]

    # increment score
    cs['score'] += sample_score(effect)

    # adjust bounds
    if cs['score'] < cs['min']:
        cs['score'] = cs['min']
    elif cs['score'] > cs['max']:
        cs['score'] = cs['max']




def apply_effects(event, current_scores):
    score_names = [s['name'] for s in current_scores]
    for effect in event.get('effects', []):
        # check to make sure score name exists
        if effect['name'] not in score_names:
            print(f"Score name {effect['name']} not found")
            raise Exception
        adjust_score(effect, current_scores)

def make_scores(combined_day_groups_final, score_constructor, people_constructor=None):
    final_groups = []
    for dg in combined_day_groups_final:

        # set up current scores
        current_scores = [s.copy() for s in score_constructor]
        for cs in current_scores:
            cs['score'] = cs['baseline']

        for event in dg:
                
            # apply event effects
            apply_effects(event, current_scores)

            if not people_constructor:
                continue
                # print("No people constructor found")
                # raise Exception
            
            # apply person effects
            if people := event.get('people'):

                for person in people:
                    # check to see if person exists
                    if person not in [p['name'] for p in people_constructor]:
                        print(f"{person} not found")
                        raise Exception
                    else:
                        # apply effects
                        person_spec = [p for p in people_constructor if p['name'] == person][0]
                        apply_effects(person_spec, current_scores)
                
        final_groups.append(dg.copy() + current_scores)
    return final_groups
    

## Sec: Post-formatting functions

def format_final_specs(day_groups, dates):
    day_groups_final = []
    for date, dg in zip(dates, day_groups):
        # print(date)
        temp_dg = []
        for s in dg:
            temp_s = s.copy()
            temp_s['start_date'] = date
            # print(date)
            # s['start_date'] = date
            for k in ['days']:
                temp_s.pop(k, None)
            temp_dg.append(temp_s)

        day_groups_final.append(temp_dg)
    return day_groups_final


## Sec: Meals
def add_recipes_to_meals(day_groups, recipes):
    for day_group in day_groups:
        for event in day_group:
            if event['category'] == 'meals':
                if not event['id'] in recipes:
                    # print(f"Recipe not found for {event['id']}")
                    continue
                    # raise Exception
                else:
                    event['recipe'] = random.choice(recipes[event['id']])

## Sec: Dataframe
                
def get_full_df(day_groups_final):
    all_events = [s for specs in day_groups_final for s in specs]
    df_all = pd.DataFrame(all_events)
    df_all.start_date.unique()
    df_all.sort_values(['start_date', 'start_time_hrs'], inplace=True)
    return df_all.set_index('start_date')

### Other

def get_sorted_pairs(day_group):
    sorted_combs = []
    for group_a, group_b in itertools.combinations(day_group, 2):
        time_a = group_a['start_time']
        time_b = group_b['start_time']
        if time_a < time_b:
            sorted_combs.append((group_a, group_b))
        else:
            sorted_combs.append((group_b, group_a))

        # now sort by precision?
    return sorted_combs