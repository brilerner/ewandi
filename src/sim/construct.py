# ruff: noqa

import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

sim_dir = (
    "/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/data/sim"
)
sys.path.append(sim_dir)

import copy
import itertools
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import rubrics
from utils.dates import get_days_from_range
from utils.hardcoded import ENTRY_PROMPT_DIVIDER
from utils.io import load_yaml_file
from utils.sampling import get_sample

# keep in mind..
# - makes sure I am copying where necessary

# improvements
# - add description checks
# - bring back format_times into preproc routine
# - set dewfault duration


DEFAULT_PRECEDENCE = 10
print_conflicts = True


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


def construct(profile="llm_v1"):
    print("\nStarting construction.")
    # setup
    profile_dir = Path(sim_dir) / "profiles" / profile
    sim_constructor = get_sim_data(profile_dir)
    dates = sim_constructor["dates"]
    event_specs = sim_constructor["specs"]["events"]
    constructor_specs = sim_constructor["specs"]["constructors"]

    # make events; make sure sensations is last
    day_groups = []
    for cat in ["scheduled", "unscheduled", "sleep", "meals", "sensations"]:
        # for cat in ["unscheduled", "sleep", "meals", "sensations"]:
        day_groups = make_day_groups(event_specs[cat], dates, existing=day_groups)
        if cat == "meals":
            add_recipes_to_meals(day_groups, sim_constructor["recipes"])
    add_rubric_values(day_groups, constructor_specs["rubrics"])  # make sure after meals
    add_people_info(day_groups, constructor_specs["people"])
    # create scores
    make_scores(day_groups, event_specs["scores"])
    # make intermediate journal entry prompts
    make_entry_prompts(day_groups, dates, profile_dir)

    # now, format for transfer
    save_for_transfer(day_groups, dates, profile_dir)

    print("Construction complete.\n")
    # save df
    df = get_full_df(day_groups)
    # # Save the DataFrame to a CSV file
    save_dir = profile_dir / "outputs" / "intermediate"
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
    csv_path = save_dir / "simulated_events.csv"
    df.to_csv(csv_path, index=True)
    # return df
    # display(df)
    # df.groupby('start_date').filter(lambda x: x.id.str.contains('head').any())
    # # do this at the end


def add_source_and_category(spec, category):
    if category == "scheduled":
        spec["source"] = "schedule"
        spec["category"] = "activity"
    elif category == "unscheduled":
        spec["source"] = "journal_entry"
        spec["category"] = "activity"
    elif category == "sensations":
        spec["source"] = "journal_entry"
        spec["category"] = "sensation"
    elif category == "sleep":
        spec["source"] = "sleep_tracker"
        spec["category"] = "sleep"
    elif category == "meals":
        spec["source"] = "food_tracker"
        spec["category"] = "meal"
    elif category == "survey":
        spec["source"] = "survey"
        spec["category"] = "survey"
    # else:
    #     print("Category not recognized")
    #     raise Exception


def save_for_transfer(day_groups, dates, profile_dir):
    keep_keys = [
        "name",
        "description",
        "category",
        "attributes",
        "start_datetime",
        "end_datetime",
        "all_day",  # should I keep?
        "location",
        "people",
        "source",
        "value",
        "unit",
        "dtype",
        "is_container",
        "is_value",
        "is_top",
    ]

    propagate_keys = [
        "start_datetime",
        "end_datetime",
        "all_day",
        "location",
        "people",
        "source",
    ]

    def clean_event(event, parent=None):
        # handle times
        if not parent:
            event["start_datetime"] = (date + event["start_time"]).isoformat(
                timespec="minutes"
            )
            event["end_datetime"] = (
                date + event["start_time"] + event["duration"]
            ).isoformat(timespec="minutes")

        # propagate
        for k in propagate_keys:
            if parent and (k in parent):
                event[k] = parent[k]

        # handle category

        if event.get("is_container"):
            if not event.get("category"):
                event["category"] = event["name"]
        elif event.get("is_value"):
            if parent and not event.get("category"):
                event["category"] = parent["name"]
        elif event["dtype"] == "text":
            event["category"] = None
        elif parent and not event.get("category"):
            event["category"] = parent["category"]
        # else:
        #     print("Category not recognized")
        #     raise Exception

        # remove keys
        for k in list(event.keys()):
            if k not in keep_keys:
                event.pop(k)

        for k in list(event.keys()):
            if not event[k]:
                event.pop(k)
        # recurse
        for attribute in event.get("attributes", []):
            clean_event(attribute, event)

    def clean_people(people):
        for person in people:
            for k in list(person.keys()):
                if k not in keep_keys:
                    person.pop(k, None)

    def get_events_breakout(day_groups):
        def breakout_event(event, all_events_breakout):
            attributes = event.pop("attributes", None)
            if attributes:
                for attribute in attributes:
                    breakout_event(attribute, all_events_breakout)
            all_events_breakout.append(event)

        all_events_nested = [s for specs in day_groups for s in specs]
        all_events_breakout = []
        for event in copy.deepcopy(all_events_nested):
            breakout_event(event, all_events_breakout)
        return all_events_breakout

    for dg, date in zip(day_groups, dates):
        for event in dg:
            event["dtype"] = "binary"
            clean_people(event.get("people", []))
            add_source_and_category(event, event["category"])
            clean_event(event)

    # break out the attributes into their own events
    all_events_nested = [s for specs in day_groups for s in specs]
    all_events_breakout = get_events_breakout(day_groups)

    final_dir = profile_dir / "outputs" / "final"
    with open(final_dir / "events_nested.json", "w") as file:
        json.dump(all_events_nested, file, indent=4, cls=CustomEncoder)
    with open(final_dir / "events_breakout.json", "w") as file:
        json.dump(all_events_breakout, file, indent=4, cls=CustomEncoder)
    pass
    # print out stored names
    # save for streamlit


def make_entry_prompts(day_groups, dates, profile_dir):
    # make prompts
    prompts = [
        make_single_entry_prompt(date, day_group)
        for date, day_group in zip(dates, day_groups)
    ]
    full_text = ENTRY_PROMPT_DIVIDER.join(prompts)

    # save
    file_name = profile_dir / "outputs" / "intermediate" / "entry_prompts.txt"
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
        "description",
        "start_datetime",
        "end_datetime",
        "people",
        "effects",
    ]

    key_strings = []
    for event in events:
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

    survey_event = [e for e in day_group if e["category"] == "survey"][0]
    survey_attributes = sorted(survey_event["attributes"], key=lambda x: x["name"])
    survey_strings = []
    for attribute in survey_attributes:
        attribute_string = (
            f"\t- {attribute['name'].capitalize()}: {attribute['value']}/10\n"
        )
        survey_strings.append(attribute_string)
    prompt += "\nEnd of Day Survey:\n" + "\n".join(survey_strings)

    return prompt


## Sec: Construct


def determine_final_day_groups(events, dates):
    day_groups = make_day_groups(events, dates)
    day_groups = deal_with_conflicts(day_groups)
    return day_groups


## Sec: Day groups


def construct_all_day_event(name, description, category):
    event = {
        "name": name,
        "description": description,
        "category": category,
        "dtype": "binary",
        "all_day": True,
    }
    format_times(event)
    return event


def add_attribute_to_event(
    parent,
    name,
    description,
    dtype,
    value=None,
    unit=None,
    category=None,
    is_container=False,
):
    """
    Parent can be an event or attribute.
    """

    # category = parent["category"]

    if "attributes" not in parent:
        parent["attributes"] = []
    elif name in [v["name"] for v in parent["attributes"]]:
        print(f"Attribute {name} already exists")
        raise Exception

    attribute_dict = {
        "name": name,
        "description": description,
        "value": value,
        "unit": unit,
        "dtype": dtype,
        "category": category,
        "is_container": is_container,
    }
    if value:
        attribute_dict["is_value"] = True
    parent["attributes"].append(attribute_dict)

    return parent["attributes"][-1]


def add_rubric_values(day_groups, rubric_constructor):
    def apply_rubrics_to_event(event):
        def rubric_check(rubric):
            if (rubric["parent"] == "TOP_LEVEL") and event.get("is_top"):
                return True
            elif rubric["parent"] == event["name"]:
                return True

        for rubric in rubric_constructor:
            if rubric_check(rubric):
                add_attribute_to_event(
                    event,
                    rubric["name"],
                    rubric["description"],
                    rubric["dtype"],
                    rubric["function"](event),
                    rubric.get("unit"),
                )
                # now recursively apply to attributes
                for attribute in event.get("attributes", []):
                    apply_rubrics_to_event(attribute)

    for dg in day_groups:
        for event in dg:
            event["is_top"] = True
            apply_rubrics_to_event(event)
    check_day_groups(day_groups)


def wrong_day(spec, date):
    check_counter = 0

    # check if the event occurs within the correct date range

    if "start_date" in spec:
        if date < spec["start_date"]:
            return True
    if "end_date" in spec:
        if date > spec["end_date"]:
            return True

    # check if event occurs on the specified day
    if days := spec.get("days"):
        valid_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        if not all([d in valid_days for d in days]):
            print("Day not recognized")
            raise Exception
        if date.strftime("%a") not in days:
            return True


def make_day_groups(events, dates, existing=None):
    def add_delay(spec, existing_event):
        spec["start_time"] = existing_event["start_time"] + spec["delay"]
        spec["end_time"] = spec["start_time"] + spec["duration"]

    def find_cause(causes, existing_for_day):
        def look_for_cause(cause, event):
            # if cause["name"] == 'onions':
            #     if event["name"] == ""
            #     print(event)
            if event["name"] == "dietary intake":
                pass
            if cause["name"] == event["name"]:
                return True
            elif attributes := event.get("attributes"):
                return any([look_for_cause(cause, a) for a in attributes])

        found_events = []
        for c in causes:
            for e in existing_for_day:
                if look_for_cause(c, e):
                    found_events.append(e)
        return found_events

    def combine_day_groups(dg1, dg2):
        combined_day_groups = []
        for d1, d2 in zip(dg1, dg2):
            combined_day_groups.append(d1 + d2)
        return combined_day_groups

    day_groups = []
    for i, date in enumerate(dates):
        day_group = []
        for spec in events:
            spec = spec.copy()
            format_times(spec)

            if causes := spec.get("causes"):
                # print(spec)
                if found_events := find_cause(causes, existing[i]):
                    use_first = random.choice(
                        found_events
                    )  # not set up for multiple causes yet
                    if "delay" in spec:
                        add_delay(spec, use_first)
                else:
                    continue

            if wrong_day(spec, date):
                continue

            # deal with probability
            if prob := spec.get("prob", 1):
                if random.random() > prob:
                    continue

            day_group.append(spec)

        day_groups.append(day_group)

    if existing:
        day_groups = combine_day_groups(day_groups, existing)

    day_groups = deal_with_conflicts(day_groups)

    check_day_groups(day_groups)

    return day_groups


def check_day_groups(day_groups):
    for dg in day_groups:
        for event in dg:
            if not event:
                raise Exception


## Sec: Conflict resolution


def deal_with_conflicts(day_groups):
    conflicts = make_conflict_groups(day_groups)
    removals = make_removal_groups(conflicts)
    return remove_conflicts(day_groups, removals)


def make_conflict_groups(day_groups):
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

    def conflict_present(s1, s2):
        time_conflict = s1["end_time"] >= s2["start_time"] >= s1["start_time"]
        prec_conflict = s1["precedence"] >= 0 and s2["precedence"] >= 0

        if time_conflict and prec_conflict:
            return True

    conflicts = []
    for dg in day_groups:
        day_conflicts = []
        if len(dg) >= 2:
            for s1, s2 in get_sorted_pairs(dg):
                if conflict_present(s1, s2):
                    day_conflicts.append((s1, s2))
        conflicts.append(day_conflicts)

    return conflicts


def make_removal_groups(conflicts):
    def sort_precision(day_conflicts):
        def get_top_precedence(specs):
            s1, s2 = specs
            return min(s1["precedence"], s2["precedence"])

        day_conflicts.sort(key=get_top_precedence)
        return day_conflicts

    removals = []
    for day_conflicts in conflicts:
        day_remove = []
        day_conflicts = sort_precision(day_conflicts)

        for s1, s2 in day_conflicts:
            id_1 = s1["name"]
            id_2 = s2["name"]
            s1_prec = s1["precedence"]
            s2_prec = s2["precedence"]

            # check if already removed
            existing_remove_ids = [s["name"] for s in day_remove]

            if id_1 in existing_remove_ids or id_2 in existing_remove_ids:
                continue
            elif s1_prec == s2_prec:
                if print_conflicts:
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
        r_ids = [s["name"] for s in r]
        day_group = [s for s in dg if s["name"] not in r_ids]
        day_groups_final.append(day_group)
    return day_groups_final


### Pre-formatting functions


def get_sim_data(profile_dir):
    def get_event_specs(events_dir):
        """
        Categories are the filepaths.
        """
        by_cat = {}
        for p in events_dir.glob("*.yaml"):
            cat_events = []
            cat = p.stem
            for event_info in load_yaml_file(p):
                event_info["category"] = cat  # needed for processing
                cat_events.append(event_info)
            by_cat[cat] = cat_events

        return by_cat

    def get_constructor_specs(constructors_dir):
        def insert_rubric_functions(rubric_constructor):
            for spec in rubric_constructor:
                spec["function"] = getattr(rubrics, spec["function"])

        pass_cats = ["diet"]

        by_cat = {}
        for p in constructors_dir.glob("*.yaml"):
            cat_events = []
            cat = p.stem
            if cat in pass_cats:
                continue
            for event_info in load_yaml_file(p):
                event_info["category"] = cat  # needed for processing
                cat_events.append(event_info)
            by_cat[cat] = cat_events

        # insert the rubric functions
        insert_rubric_functions(by_cat["rubrics"])

        return by_cat

    def get_dates(sim_params):
        sim_dates = sim_params.get("dates")
        for k in sim_dates:
            sim_params["dates"][k] = convert_date(sim_dates[k])
        dates = get_days_from_range(sim_dates["start_date"], sim_dates["end_date"])
        return dates

    def load_sim_params(sim_params_path):
        sim_params = load_yaml_file(sim_params_path)
        return sim_params

    def load_recipes(recipes_path):
        recipes = load_yaml_file(recipes_path)
        return recipes

    def validate_people(spec):
        if people := spec.get("people"):
            if isinstance(people, str):
                spec["people"] = [people]
            elif isinstance(people, list):
                if len(people) == 0:
                    print("People not recognized")
                    raise Exception
            else:
                print("People not recognized")
                raise Exception

    def handle_precedence(spec):
        if spec["category"] == "sleep":
            if "precedence" in spec:
                print("CONFLICT: sleep w/ precedence")
                raise Exception
            spec["precedence"] = 0
        if spec["category"] == "scores":
            if "precedence" in spec:
                print("CONFLICT: scores w/ precedence")
                raise Exception
            spec["precedence"] = -1
        if spec["category"] == "meals":
            if "precedence" in spec:
                print("CONFLICT: meals w/ precedence")
                raise Exception
            spec["precedence"] = -1
        if spec["category"] == "sensations":
            if "precedence" in spec:
                print("CONFLICT: sensations w/ precedence")
                raise Exception
            spec["precedence"] = -1
        if spec["category"] == "scheduled":
            if "precedence" not in spec:
                spec["precedence"] = DEFAULT_PRECEDENCE
        if spec["category"] == "unscheduled":
            if "precedence" not in spec:
                spec["precedence"] = DEFAULT_PRECEDENCE

    def validate_spec(spec):
        if not spec.get("name"):
            print("Need name")
            raise Exception
        if not spec.get("description"):
            print("Need description")
            raise Exception
        validate_people(spec)
        handle_precedence(spec)

    # set up paths
    recipes_path = profile_dir / "outputs" / "intermediate" / "recipes.json"
    inputs_dir = profile_dir / "inputs"

    # fill in sim constructor
    sim_constructor = {}
    # set up sim params and dates
    sim_constructor["sim_params"] = load_sim_params(inputs_dir / "sim_params.yaml")
    sim_constructor["dates"] = get_dates(sim_constructor["sim_params"])

    # set up recipes
    sim_constructor["recipes"] = load_recipes(recipes_path)

    sim_constructor["specs"] = {
        "events": get_event_specs(inputs_dir / "events"),
        "constructors": get_constructor_specs(inputs_dir / "constructors"),
    }

    # validate/format events
    for category, specs in sim_constructor["specs"]["events"].items():
        for spec in specs:
            validate_spec(spec)  # make code to check rest of variables
            format_dates(spec, sim_constructor["sim_params"]["dates"])

    # validate/format constructors
    for category, specs in sim_constructor["specs"]["constructors"].items():
        for spec in specs:
            validate_spec(spec)  # make code to check rest of variables

    return sim_constructor


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


def format_dates(spec, sim_params):
    if not spec.get("start_date"):
        spec["start_date"] = sim_params["start_date"]
    else:
        spec["start_date"] = convert_date(spec["start_date"], sim_params)
    if not spec.get("end_date"):
        spec["end_date"] = sim_params["end_date"]
    else:
        spec["end_date"] = convert_date(spec["end_date"], sim_params)
    if spec["start_date"] > spec["end_date"]:
        print("Start date comes before end date.")
        raise


### Timing functions


def convert_date(date_string, sim_params=None):
    if sim_params is not None and "PH" in date_string:
        date_string = date_string.replace("PH_", "")
        return sim_params[date_string]
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


# Sec: Causes


## Sec: Effects


def add_people_info(day_groups, people_constructor):
    def add_people_to_event(event):
        existing_people = [p["name"] for p in people_constructor]
        if event_people := event.get("people"):
            if any([p not in existing_people for p in event_people]):
                print("Person not found")
                raise Exception
            event["people"] = [
                p for p in people_constructor if p["name"] in event_people
            ]

    for dg in day_groups:
        for event in dg:
            add_people_to_event(event)
    check_day_groups(day_groups)


def make_scores(day_groups, score_constructor):
    def get_current_scores():
        current_scores = copy.deepcopy(score_constructor)
        for s in current_scores:
            format_times(s)
            s["score"] = s["baseline"]
        return current_scores

    def apply_effects_to_event(event, current_scores):
        def adjust_score(effect, current_scores):
            for cs in current_scores:
                if cs["name"] == effect["name"]:
                    break

            # increment score
            cs["score"] += get_sample(effect["vals"], effect.get("probs"))

            # adjust bounds
            if cs["score"] < cs["min"]:
                cs["score"] = cs["min"]
            elif cs["score"] > cs["max"]:
                cs["score"] = cs["max"]

        score_names = [s["name"] for s in current_scores]
        for effect in event.get("effects", []):
            # check to make sure score name exists
            if effect["name"] not in score_names:
                print(f"Score name {effect['name']} not found")
                raise Exception
            adjust_score(effect, current_scores)

        for people in event.get("people", []):
            for effect in people.get("effects", []):
                adjust_score(effect, current_scores)

        # now recursively apply to attributes
        for attribute in event.get("attributes", []):
            apply_effects_to_event(attribute, current_scores)

    def create_survey_event(current_scores):
        survey_event = construct_all_day_event(
            "daily recap",
            "A survey performed at the end of the day to assess mood, energy, and stress.",
            "survey",
        )
        for c in current_scores:
            add_attribute_to_event(
                survey_event,
                c["name"],
                c["description"],
                "numerical",
                c["score"],
                "arbitrary",
            )
        return survey_event

    for dg in day_groups:
        current_scores = get_current_scores()
        for event in dg:
            apply_effects_to_event(event, current_scores)
        survey_event = create_survey_event(current_scores)
        dg.append(survey_event)
    check_day_groups(day_groups)


## Sec: Meals
def add_recipes_to_meals(day_groups, recipes):
    def add_recipe_to_event(event, recipe):
        """
        Add recipe name as a value, but keep hidden.
        """
        choices = [k.lower() for k in recipes.keys()]  # breakfast, lunch, etc

        if event["name"].lower() not in choices:
            print(f"Recipe not found for {event['nid']}")
            raise Exception

        recipe_choice = random.choice(recipes[event["name"]]).copy()

        # add dietary intake
        dietary_intake = add_attribute_to_event(
            event,
            "dietary intake",
            "The ingredients consumed.",  # the description
            "binary",
            is_container=True,
        )

        # now add recipe name as a subattribute
        add_attribute_to_event(
            dietary_intake,
            recipe_choice.pop("name"),
            "The name of the recipe consumed.",
            "text",
        )

        # now calories
        add_attribute_to_event(
            dietary_intake,
            "calories",
            "The number of calories consumed.",
            "numerical",
            recipe_choice.pop("calories"),
            "calorie",
        )

        # now add ingredients # CONFIRM THIS IS RIGHTTTTTTT
        ingredients = recipe_choice.pop("ingredients")
        for ingredient in ingredients:
            add_attribute_to_event(
                dietary_intake,
                ingredient,
                "The name of the ingredient consumed.",
                "binary",
            )

    for day_group in day_groups:
        for event in day_group:
            if event["category"] == "meals":
                add_recipe_to_event(event, recipes)
    check_day_groups(day_groups)


## Sec: Dataframe


def get_full_df(day_groups_final):
    all_events = [s for specs in day_groups_final for s in specs]
    df = pd.DataFrame(all_events)

    # order = [
    #     "start_datetime",
    #     "end_datetime",
    #     "name",
    #     # 'duration',
    #     "score",
    #     "groups",
    # ]

    # reordered_columns = []
    # for k in order:
    #     if k in df.columns:
    #         reordered_columns.append(k)
    # for k in df.columns:
    #     if k not in order:
    #         reordered_columns.append(k)
    # df = df[reordered_columns]
    # # df_all.sort_values(['start_date', 'start_time_hrs'], inplace=True)

    # day_strings = df["start_datetime"].apply(lambda x: x.strftime("%a"))
    # df.insert(0, "day", day_strings)

    return df.sort_values("start_datetime")  # .set_index('start_date')


### Other


if __name__ == "__main__":
    profile = "llm_v1"
    # profile = 'simple'

    construct(profile)
