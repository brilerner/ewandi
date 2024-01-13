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
