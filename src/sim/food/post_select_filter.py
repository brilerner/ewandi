import json
from pathlib import Path

import yaml

ENERGY_NAME = "energy"  # no need for multiple types of conversions
ENERGY_UNITS = "kcal"


food_data_dir = Path(
    "/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/Cerebra/data/sim/foods"
)


def load_foods():
    path = food_data_dir / "foundationDownload.json"
    foods = json.load(open(path))["FoundationFoods"]
    return foods


skip_strings = [
    "restaurant",
    "added",
    "moisture",
    "bleached",
    "enriched",
    "all-purpose",
    "long grain",
    "grade",
    "prepared",
    "raw",
    "bone",
    "skin",
    "prepared",
    "ready",
    "flesh",
    "whole",
    "drained",
    "canned",
    "light",
    "fluid",
    "block",
    "choice",
    "bleach" "stick" "part",
    "grated",
    "fat",
    "full",
    "dark",
    "navels",
    "honeycrisp",
    "bartlett",
    "commercial",
    "mild",
    "breakfast",
    "snap",
    "baby",
    "peel",
    "red",
    "seedless",
    "part-skim",
    "yellow",
    "dry",
    "restaurant",
    "large",
    "kernel",
    "iodized",
    "green",
    "table",
    "iceberg",
    "shiitake",
    "russet",
    "roma",
    "spaghetti",
    "breast",
    "extra virgin",
    "plain",
    "unsalted",
    "wheat",
    "white",
    "flank",
    "steel cut",
    "stick",
    "creamy",
    "beef",
]

keep_strings = ["strawberries", "mustard", "peach", "kiwi"]

remove_strings = ["Seeds", "Nuts"]


def format_name(name):
    def check_name(p):
        for s in keep_strings:
            if s in p.lower():
                return True

        for s in skip_strings:
            if s in p.lower():
                return False
        return True

    def remove_part(p):
        for s in remove_strings:
            if s in p:
                return False
        return True

    name = name.split("(")[0].strip()
    parts = [
        p.strip().lower() for p in name.split(",") if remove_part(p) and check_name(p)
    ]

    if len(parts) > 2:
        raise ValueError("More than two parts in name")
    elif len(parts) == 0:
        raise ValueError("No parts in name")
    elif len(parts) == 2:
        parts = parts[::-1]
        return " ".join(parts).lower()
    else:
        return parts[0]

    # return ", ".join(parts).lower()


def add_energy(foods):
    def get_energy_occurrences(food):
        def check_nutrient(nutrient):
            if "Energy" in nutrient["name"]:
                return True
            else:
                return False

        energy_occurrences = []
        for f in food["foodNutrients"]:
            if check_nutrient(f["nutrient"]):
                energy_occurrences.append(f)
        return energy_occurrences

    def check_energy_occurrences(food, energy_occurrences):
        # check if there are multiple values for energy or missing amounts
        if len(energy_occurrences) == 0:
            print("Not a single energy value for", food["description"])
            return False
        elif len(energy_occurrences) >= 2:
            print("More than one energy value for", food["description"])
            return False

    # only care about energy for now to avoid issues with other nutrients
    filtered_foods = []
    for food in foods:
        energy_occurrences = get_energy_occurrences(food)
        if not check_energy_occurrences(food, energy_occurrences):
            continue
        else:
            filtered_foods.append(
                {
                    "description": food["description"],
                    "nutrients": [
                        {
                            "name": ENERGY_NAME,
                            "unit": ENERGY_UNITS,
                            "amount": energy_occurrences[0]["amount"],
                        }
                    ],
                }
            )
    return filtered_foods


def match_foods(foods_full, selected_foods):
    # now, save new food file
    selected_foods_list = [f for cat in selected_foods.values() for f in cat]
    foods = []
    for food in foods_full:
        for sf in selected_foods_list:
            if food["description"] == sf[0]:
                food["name"] = sf[1]
                foods.append(food)
                break
    return foods


def post_select_filter():
    def reformat_names(names):
        new_names = []
        for n in names:
            formatted_name = format_name(n)
            if formatted_name == "":
                raise ValueError("Empty name")
            # new_names.append([n, formatted_name])
            new_names.append(format_name(n))
        return new_names

    with open(food_data_dir / "food_names_KEEP.yaml", "r") as file:
        selected_foods = yaml.safe_load(file)
    foods_full = load_foods()

    # reformat names
    for category, names in selected_foods.items():
        selected_foods[category] = reformat_names(names)

    # match foods
    foods = match_foods(foods_full, selected_foods)

    # # add energy
    # foods = add_energy(foods)

    # save
    with open(food_data_dir / "food_names_filtered.yaml", "w") as outfile:
        yaml.dump(selected_foods, outfile)

    with open(food_data_dir / "foods_filtered.json", "w") as outfile:
        json.dump(foods, outfile)


if __name__ == "__main__":
    post_select_filter()
