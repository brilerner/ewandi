import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src":
    src_dir = src_dir.parent
sys.path.append(str(src_dir))
import copy
import itertools
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from utils.dates import get_days_from_range
from utils.hardcoded import ENTRY_PROMPT_DIVIDER
from utils.io import load_json, load_yaml_file

# keep in mind..
# - makes sure I am copying where necessary

# improvements
# - add description checks
# - bring back format_times into preproc routine
# - set dewfault duration

# inputs_dir = Path.cwd().parent.parent /'data'/'sim' / 'profiles'/profile/'inputs'

profile = "llm_v1"
profile_dir = f"/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/ewandi/data/sim/profiles/{profile}"
inputs_dir = Path(profile_dir) / "inputs"
sys.path.append(inputs_dir)

sim_path = "/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/ewandi/data/sim"
sys.path.append(sim_path)
import rubrics.rubrics as rubrics

DEFAULT_PRECEDENCE = 10


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


def construct(profile="llm_v1"):
    profile_dir = Path(
        f"/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/ewandi/data/sim/profiles/{profile}"
    )
    inputs_dir = profile_dir / "inputs"
    outputs_dir = Path(profile_dir) / "outputs"
    final_dir = outputs_dir / "final"

    sim_params_path = inputs_dir / "sim_params.yaml"
    sim_params = load_yaml_file(sim_params_path)
    sim_dates = sim_params.get("dates")
    for k in sim_dates:
        sim_params["dates"][k] = convert_date(sim_dates[k])
    dates = get_days_from_range(sim_dates["start_date"], sim_dates["end_date"])

    args = {
        "sim_params": sim_params,
        "dates": dates,
        "inputs_dir": inputs_dir,
        "outputs_dir": outputs_dir,
    }

    recipes_path = outputs_dir / "intermediate" / "recipes_final.json"
    recipes = load_json(recipes_path)

    # get rubrics
    rubric_specs = load_yaml_file(inputs_dir / "rubrics.yaml")
    for spec in rubric_specs:
        spec["function"] = getattr(rubrics, spec["function"])

    # setup
    specs = get_specs(args, profile)
    prepare_specs(specs, args)

    # scheduled events
    combined_day_groups = determine_final_day_groups(specs["scheduled"], dates)
    print()
    # unscheduled events
    day_groups_final_unscheduled = determine_final_day_groups(
        specs["unscheduled"], dates
    )
    combined_day_groups = combine_day_groups(
        combined_day_groups, day_groups_final_unscheduled
    )
    combined_day_groups = deal_with_conflicts(combined_day_groups)

    # add meals
    day_groups_meals = make_day_groups(specs["meals"], dates)
    add_recipes_to_meals(day_groups_meals, recipes)
    combined_day_groups = combine_day_groups(combined_day_groups, day_groups_meals)

    # add sleep
    day_groups_sleep = make_day_groups(specs["sleep"], dates, rubric_specs=rubric_specs)
    combined_day_groups = combine_day_groups(combined_day_groups, day_groups_sleep)

    # add sensations
    day_groups_sensations = make_day_groups(
        specs["sensations"], dates, existing_events=combined_day_groups
    )
    combined_day_groups = combine_day_groups(combined_day_groups, day_groups_sensations)

    # create scores
    final_groups = make_scores(
        combined_day_groups,
        score_constructor=specs["scores"],
        people_constructor=specs["people"],
    )

    # add people descriptions
    add_people_descriptions(final_groups, specs["people"])

    final_groups = format_final_specs(final_groups, dates)

    # make intermediate journal entry prompts
    make_entry_prompts(dates, final_groups, args)

    # now, format for transfer
    save_for_transfer(final_groups, final_dir)

    df = get_full_df(final_groups)

    # Save the DataFrame to a CSV file
    save_dir = profile_dir / "outputs" / "intermediate"
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
    csv_path = save_dir / "simulated_events.csv"
    df.to_csv(csv_path, index=False)
    return df
    # display(df)
    # df.groupby('start_date').filter(lambda x: x.id.str.contains('head').any())
    # # do this at the end


def add_people_descriptions(final_groups, people_specs):
    for day_group in final_groups:
        for event in day_group:
            if people := event.get("people"):
                refmtd_people = []
                for person in people:
                    person_spec = [p for p in people_specs if p["name"] == person][0]
                    refmtd_people.append(
                        {
                            "name": person_spec["name"],
                            "role": person_spec["role"],
                            "description": person_spec.get(
                                "description", person_spec["role"]
                            ),
                        }
                    )
                event["people"] = refmtd_people


def save_for_transfer(final_groups, final_dir):
    """
    I will save all events int the following sections. If I want to do RAG, I will try to
    save the entry as an attribute of the event (content)

    Meals
    - calories
    - save as value
    """

    keep_keys = [
        "nid",
        "name",
        "category",
        "description",
        "start_datetime",
        "end_datetime",
        "all_day",
        # 'duration',
        "location",
        "people",
        "intake",
        "score",
        "content",
        "values",
    ]
    all_events = []
    i = 0
    for day_group in final_groups:
        for event in day_group:
            # if event['name'] == 'sleep':
            #     print()
            event = copy.deepcopy(event)
            event = {k: v for k, v in event.items() if k in keep_keys}
            i += 1
            event["start_datetime"] = event["start_datetime"].isoformat()
            event["end_datetime"] = event["end_datetime"].isoformat()

            if event["category"] == "scores":
                if "values" not in event:
                    event["values"] = [
                        {
                            "name": "level",
                            "value": event["score"],
                            "unit": "arb",
                            "type": "int",
                            "description": f"{event['name'].capitalize()} level for the day.",
                            "nid": f"{event['name']}.level",
                        }
                    ]
                event.pop("score", None)

            if event["category"] == "unscheduled":
                event["source"] = "journal_entry"
            if event["category"] == "sensations":
                event["source"] = "journal_entry"

            # if 'rubric_value' in event:
            #     event['values'] = [
            #         {'name': 'rubric_value', 'value': event['rubric_value'], 'unit':'arb', 'type':'int'}
            #     ]
            #     event.pop('rubric_value', None)

            # if event['category'] == 'meals':
            #     pass
            all_events.append(event)

    file_name = final_dir / "events.json"
    with open(file_name, "w") as file:
        json.dump(all_events, file, indent=4, cls=CustomEncoder)


def make_entry_prompts(dates, final_groups, args):
    # make prompts
    prompts = [
        make_single_entry_prompt(date, day_group)
        for date, day_group in zip(dates, final_groups)
    ]
    full_text = ENTRY_PROMPT_DIVIDER.join(prompts)

    # save
    file_name = args["outputs_dir"] / "intermediate" / "entry_prompts.txt"
    with open(file_name, "w") as file:
        file.write(full_text)


def make_single_entry_prompt(date, day_group):
    def parse_effects_for_entry(effects):
        effects_text = ""
        effects_conventions = {
            "energy": {"+": "increased", "-": "decreased"},
            "mood": {"+": "better", "-": "worse"},
            "stress": {"+": "increased", "-": "decreased"},
        }
        effect_strings = []
        for effect in effects:
            value = effect["vals"][0]
            if value > 0:
                effect_text = "{modifier} {effect}\n".format(
                    modifier=effects_conventions[effect["name"]]["+"], effect=effect
                )
            elif value < 0:
                effect_text = "{modifier} {effect}\n".format(
                    modifier=effects_conventions[effect["name"]]["-"], effect=effect
                )
            effect_strings.append(effect_text)
        effects_text = ", ".join(effect_strings)

        return effects_text

    # determine which categories to keep
    keep_cats = ["scheduled", "unscheduled", "sensations"]

    # Write the date and day of the week
    day_of_week = date.strftime("%A")

    # begin prompt
    prompt = f"Date: {date} ({day_of_week})\n\n"

    # add events if in keep_cats
    events = [e for e in day_group if e["category"] in keep_cats]
    # sort events by start time
    # events = sorted(events, key=lambda e: e['start_datetime'])

    keep_keys = [
        "name",
        "location",
        "start_datetime",
        "end_datetime",
        "people",
        "effects",
    ]

    key_strings = []
    for event in day_group:
        # add name first
        name_string = "{}: {}\n".format("Name", event["name"])
        key_strings.append(name_string)
        # process the rest
        for key in keep_keys[:1]:
            # only record key if it exists
            if value := event.get(key):
                if key == "people":
                    value = ", ".join(value)
                elif key == "effects":
                    value = parse_effects_for_entry(value)
                elif key in ["start_datetime", "end_datetime"]:
                    value = value.strftime("%H:%M")

                key_string = f"\t- {key.capitalize()}: {value.capitalize()}\n"
                key_strings.append(key_string)
    prompt += "\n".join(key_strings)

    return prompt


def get_specs(args, profile="llm_v1"):
    specs = []
    by_cat = {}
    for p in args["inputs_dir"].glob("*.yaml"):
        if "sim_params" in p.name:
            continue

        cat = p.stem
        cat_events = load_yaml_file(p)

        for event_info in cat_events:
            event_info["category"] = cat
            if "calendar" in cat:
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


def make_day_groups(events, dates, rubric_specs=None, existing_events=None):
    day_groups = []
    for i, date in enumerate(dates):
        day_group = []
        for spec in events:
            spec = spec.copy()
            format_times(
                spec
            )  # later, bring this back into main preproc routine with format_dates

            if not check_day(spec, date):
                continue
            if existing_events:
                if "causes" not in spec:
                    continue
                if not check_causes(spec, existing_events[i]):
                    continue
            # deal with probability
            if prob := spec.get("prob", 1):
                if random.random() > prob:
                    continue

            # add to rubric make into own function later
            if rubric_specs:
                rubric_names = [r["name"] for r in rubric_specs]
                if spec["name"] in rubric_names:
                    rubric_spec = [
                        r for r in rubric_specs if r["name"] == spec["name"]
                    ][0]
                    rubric_func = rubric_spec["function"]
                    if "values" not in spec:
                        spec["values"] = []
                    spec["values"].append(rubric_func(spec))

            day_group.append(spec)

        day_groups.append(day_group)

    return day_groups


def combine_day_groups(dg1, dg2):
    combined_day_groups = []
    for d1, d2 in zip(dg1, dg2):
        combined_day_groups.append(d1 + d2)
    return combined_day_groups


## Sec: Conflict resolution


def deal_with_conflicts(day_groups):
    conflicts = make_conflict_groups(day_groups)
    removals = make_removal_groups(conflicts)
    return remove_conflicts(day_groups, removals)


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
        if len(dg) >= 2:
            for s1, s2 in get_sorted_pairs(dg):
                id_1 = s1["nid"]
                id_2 = s2["nid"]
                if s1["end_time"] >= s2["start_time"] >= s1["start_time"]:
                    # to make sorting precision easier later
                    if (
                        s1.get("precedence", DEFAULT_PRECEDENCE) < 0
                        or s2.get("precedence", DEFAULT_PRECEDENCE) < 0
                    ):
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

        for s1, s2 in day_conflicts:
            id_1 = s1["nid"]
            id_2 = s2["nid"]
            s1_prec = s1.get("precedence", DEFAULT_PRECEDENCE)
            s2_prec = s2.get("precedence", DEFAULT_PRECEDENCE)

            # check if already removed
            existing_remove_ids = [s["nid"] for s in day_remove]

            if id_1 in existing_remove_ids or id_2 in existing_remove_ids:
                continue
            elif s1_prec == s2_prec:
                print(f"Precedence conflict:{id_1}, {id_2}")
                # choose conflict randomly
                remove_spec = [s1, s1][round(random.random())]
            elif s1_prec > s2_prec:
                remove_spec = s1
            else:
                remove_spec = s2
            # remove_id = remove_spec['nid']
            day_remove.append(remove_spec)
        removals.append(day_remove)
    return removals


def remove_conflicts(day_groups, removals):
    day_groups_final = []
    for r, dg in zip(removals, day_groups):
        # print*
        r_ids = [s["nid"] for s in r]
        day_group = [s for s in dg if s["nid"] not in r_ids]
        day_groups_final.append(day_group)
    return day_groups_final


### Pre-formatting functions


def prepare_specs(specs, args):
    def check_description(spec):
        if not spec.get("description"):
            print("Need description")
            raise Exception

    process_dates = ["scheduled", "sensations", "unscheduled", "scores", "sleep"]
    # process_times = process_dates + ["meals"]
    for category, specs in specs.items():
        for spec in specs:
            check_description(spec)
            spec["category"] = category
            if category in process_dates:
                format_dates(spec, args)
            # if category in process_times:
            #     format_times(spec)


def handle_duration(spec):
    def is_sampled_dict(arg):
        if isinstance(arg, dict) and "vals" in arg:
            return True
        return False

    duration = spec["duration"]
    if is_sampled_dict(duration):
        duration_choice = get_sample(duration["vals"], duration.get("probs"))
        spec["duration"] = duration_choice["val"]

        if effects := duration_choice.get("effects"):
            for effect in effects:
                effect_value = get_sample(effect["vals"], effect.get("probs"))

                if spec_effects := spec.get("effects"):
                    for spec_effect in spec_effects:
                        if spec_effect["name"] == effect["name"]:
                            spec_effect["vals"] = [
                                v + effect_value for v in spec_effect["vals"]
                            ]
                        else:
                            spec["effects"].append(effect)
                else:
                    spec["effects"] = [effect]


def handle_all_day(spec):
    # deal with conflicts
    if spec.get("start_time") or spec.get("duration"):
        if spec.get("start_time"):
            print("CONFLICT: all_day w/ start_time")
            raise Exception
        if spec.get("end_time"):
            print("CONFLICT: all_day w/ end_time")
            raise Exception
        if spec.get("duration"):
            print("CONFLICT: all_day w/ duration")
            raise Exception
        if spec.get("delay"):
            print("CONFLICT: all_day w/ delay")
            raise Exception


def handle_delay(spec):
    if spec.get("all_day"):
        print("CONFLICT: delay w/ all_day")
        raise Exception
    if spec.get("start_time"):
        print("CONFLICT: all_day w/ start_time")
        raise Exception
    if spec.get("end_time"):
        print("CONFLICT: all_day w/ end_time")
        raise Exception
    if not spec.get("duration"):
        print("Need duration")
        raise Exception


def handle_normal(spec):
    if not spec.get("start_time"):
        print("Need start time")
        print(spec)
        raise Exception
    if not spec.get("duration"):
        print("Need duration")
        raise Exception


def define_times(spec, event_type):
    # print(spec)
    # print()

    if event_type != "delay":
        spec["start_time"] = convert_start_time(spec["start_time"])
        spec["start_time_hrs"] = spec["start_time"].total_seconds() / 60**2
        spec["end_time"] = convert_end_time(spec["duration"], spec["start_time"])
        spec["end_time_hrs"] = spec["end_time"].total_seconds() / 60**2
    else:
        spec["delay"] = timedelta(**spec["delay"])

    spec["duration"] = timedelta(**spec["duration"])


def format_times(spec):
    if spec.get("all_day"):
        handle_all_day(spec)
        # set times
        spec["start_time"] = "00:00:00"
        spec["duration"] = {"days": 1}
        define_times(spec, "all_day")
    else:
        if spec.get("delay"):
            handle_delay(spec)
            handle_duration(spec)
            define_times(spec, "delay")
        else:
            handle_normal(spec)
            handle_duration(spec)
            define_times(spec, "normal")


def format_dates(spec, args):
    # set up dates
    # if spec['name'] == 'Game':
    #     print()
    if not spec.get("start_date"):
        spec["start_date"] = args["sim_params"]["dates"]["start_date"]
    else:
        spec["start_date"] = convert_date(spec["start_date"], args)
    if not spec.get("end_date"):
        spec["end_date"] = args["sim_params"]["dates"]["end_date"]
    else:
        spec["end_date"] = convert_date(spec["end_date"], args)
    if spec["start_date"] > spec["end_date"]:
        print("Start date comes before end date.")
        raise


### Timing functions


def convert_date(date_string, args=None):
    if args is not None and "PH" in date_string:
        date_string = date_string.replace("PH_", "")
        return args["sim_params"]["dates"][date_string]
    else:
        return datetime.strptime(date_string, "%Y-%m-%d")


def convert_start_time(time_string):
    t = timedelta()
    parts = (p for p in ["hours", "minutes", "seconds"])
    for p in time_string.split(":"):
        t += timedelta(**{next(parts): float(p)})
    return t


def convert_end_time(duration, start_time):
    return start_time + timedelta(**duration)


### Validation functions


def check_day(spec, date):
    check_counter = 0

    # check if the event occurs within the correct date range

    if "start_date" in spec:
        if date < spec["start_date"]:
            check_counter += 1
    if "end_date" in spec:
        if date > spec["end_date"]:
            check_counter += 1

    # check if event occurs on the specified day
    if days := spec.get("days"):
        valid_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        if not all([d in valid_days for d in days]):
            print("Day not recognized")
            raise Exception
        # if spec['name'] == 'Game':
        #     print()
        if date.strftime("%a") not in days:
            check_counter += 1

    if check_counter == 0:
        return True
    else:
        return False


# Sec: Causes


def check_single_cause(cause, existing_events_for_day):
    cause_types = ["ingredient", "standard"]

    cause_type = cause.get("type", "standard")
    # if cause_type == 'ingredient':
    #     print()
    if cause_type not in cause_types:
        print("cause type not recognized")
        raise Exception

    for existing_event in existing_events_for_day:
        if cause_type == "ingredient":
            if intake := existing_event.get("intake"):
                ingredient_names = [i["name"] for i in intake["ingredients"]]
                if cause["name"] in ingredient_names:
                    return existing_event
        elif cause_type == "standard":
            if existing_event["name"] == cause["name"]:
                return existing_event
    return None  # this means no cause was found


def check_causes(spec, existing_events_for_day):
    cause = spec["causes"][0]  # not set up for multiple causes yet
    if existing_event := check_single_cause(cause, existing_events_for_day):
        if "delay" in spec:
            spec["start_time"] = existing_event["start_time"] + spec["delay"]
            spec["end_time"] = spec["start_time"] + spec["duration"]
        return True
    else:
        return False


## Sec: Effects


def adjust_score(effect, current_scores):
    # get current score for effect
    cs = [cs for cs in current_scores if cs["name"] == effect["name"]][0]

    # increment score
    cs["score"] += get_sample(effect["vals"], effect.get("probs"))

    # adjust bounds
    if cs["score"] < cs["min"]:
        cs["score"] = cs["min"]
    elif cs["score"] > cs["max"]:
        cs["score"] = cs["max"]


def apply_effects(event, current_scores):
    score_names = [s["name"] for s in current_scores]
    for effect in event.get("effects", []):
        # check to make sure score name exists
        if effect["name"] not in score_names:
            print(f"Score name {effect['name']} not found")
            raise Exception
        adjust_score(effect, current_scores)


def make_scores(combined_day_groups_final, score_constructor, people_constructor=None):
    final_groups = []
    for dg in combined_day_groups_final:
        # set up current scores
        current_scores = []
        for s in score_constructor:
            s = s.copy()
            format_times(s)
            s["score"] = s["baseline"]
            current_scores.append(s)

        for event in dg:
            # apply event effects
            apply_effects(event, current_scores)

            if not people_constructor:
                continue
                # print("No people constructor found")
                # raise Exception

            # apply person effects
            if people := event.get("people"):
                for person in people:
                    # check to see if person exists
                    if person not in [p["name"] for p in people_constructor]:
                        print(f"{person} not found")
                        raise Exception
                    else:
                        # apply effects
                        person_spec = [
                            p for p in people_constructor if p["name"] == person
                        ][0]
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
            s = s.copy()

            # format date
            s["start_datetime"] = date + s["start_time"]
            s["end_datetime"] = s["start_datetime"] + s["duration"]

            temp_dg.append(s)

        day_groups_final.append(temp_dg)

    return day_groups_final


## Sec: Meals
def add_recipes_to_meals(day_groups, recipes):
    for day_group in day_groups:
        for event in day_group:
            if event["category"] == "meals":
                if event["nid"] not in recipes:
                    # print(f"Recipe not found for {event['nid']}")
                    continue
                    # raise Exception
                else:
                    recipe_choice = random.choice(recipes[event["nid"]])
                    recipe_choice = recipe_choice.copy()
                    recipe_choice.pop("name", None)

                    if "kcal" in recipe_choice:
                        if "values" not in event:
                            event["values"] = [
                                {
                                    "name": "calories",
                                    "value": round(recipe_choice.pop("kcal")),
                                    "unit": "calorie",
                                    "type": "int",
                                    "nid": f"{event['name']}.calories",
                                }
                            ]

                    event["intake"] = recipe_choice


## Sec: Dataframe


def get_full_df(day_groups_final):
    all_events = [s for specs in day_groups_final for s in specs]
    df = pd.DataFrame(all_events)

    order = [
        "start_datetime",
        "end_datetime",
        "nid",
        # 'duration',
        "score",
        "groups",
    ]

    reordered_columns = []
    for k in order:
        if k in df.columns:
            reordered_columns.append(k)
    for k in df.columns:
        if k not in order:
            reordered_columns.append(k)
    df = df[reordered_columns]
    # df_all.sort_values(['start_date', 'start_time_hrs'], inplace=True)

    day_strings = df["start_datetime"].apply(lambda x: x.strftime("%a"))
    df.insert(0, "day", day_strings)

    return df.sort_values("start_datetime")  # .set_index('start_date')


### Other


def get_sample(values, probabilities=None):
    return np.random.choice(values, p=probabilities)


def get_sorted_pairs(day_group):
    sorted_combs = []
    for group_a, group_b in itertools.combinations(day_group, 2):
        time_a = group_a["start_time"]
        time_b = group_b["start_time"]
        if time_a < time_b:
            sorted_combs.append((group_a, group_b))
        else:
            sorted_combs.append((group_b, group_a))

        # now sort by precision?
    return sorted_combs


if __name__ == "__main__":
    profile = "llm_v1"
    # profile = 'simple'

    df = construct(profile)
    print(df)

    # # parse args
    # argparser = argparse.ArgumentParser(description='Simulate a profile')
    # argparser.add_argument('--profile', type=str, default='llm_v0', help='Profile to simulate')
    # # argparser.add_argument('--make_events', action='store_true', help='Make events')
    # argparser.add_argument('--entries', action='store_true', help='Make journal entries')
    # argparser.add_argument('--reset', action='store_true', help='Reset profile')
    # argparser.add_argument('--transfer', action='store_true', help='Transfer profile')
    # args = argparser.parse_args()


# s['start_date'] = date

# # remove keys
# remove_list = [
#             'days',
#             # 'all_day',
#             'start_time',
#             'start_time_hrs',
#             'end_time',
#             'end_time_hrs',
#             'start_date',
#             'end_date',
#             'delay',
#             'prob',
#             'causes',
#             'effects',
#             # 'recipe',
#             'precedence',
#             'baseline',
#             'max',
#             'min'
# ]
# for k in remove_list:
#     s.pop(k, None)

# reorder keys


# order = [
#     'nid',
#     'score',
#     'start_datetime',
#     'end_datetime',
#     'duration',
#     'groups',
#     'intake'
# ]

# if 'score' in s:
#     print()
# reordered_s = {}
# for k in order:
#     if k in s:
#         if 'score' in s:
#             print()
#         reordered_s[k] = s[k]

# for k in s:
#     if k not in order:
#         reordered_s[k] = s[k]
# s = reordered_s

# def handle_duration(spec):
#     duration = spec['duration']
#     if mode := duration.get('mode'):
#         if mode == 'sampled':
#             # pick  a duration
#             indices = [i for i in range(len(duration['vals']))]
#             chosen_index = get_sample(indices, duration.get('probs'))
#             spec['duration'] = duration['vals'][chosen_index]
#             # pick effects
#             if effects := spec.get('effects'):
#                 updated_effects = []
#                 for effect in effects:
#                     if 'sampled' in effect:
#                         chosen_effect = effect['sampled'][chosen_index]
#                         effect.update(chosen_effect)
#                         del effect['sampled']
#                     updated_effects.append(effect)
#                 spec['effects'] = updated_effects
#                 print()
#         else:
#             print("Mode not recognized")
#             raise Exception
#     else:
#         # handle effect mode
#         if effects := spec.get('effects'):
#             for effect in effects:
#                 if 'sampled' in effect:
#                     print("Effects sampled but no mode specified")
#                     raise Exception
