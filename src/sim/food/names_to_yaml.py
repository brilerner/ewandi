import json
from pathlib import Path

import yaml

food_data_dir = Path(
    "/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/Cerebra/data/sim/foods"
)


def load_foods():
    path = food_data_dir / "foundationDownload.json"
    foods = json.load(open(path))["FoundationFoods"]
    return foods


def get_foods_by_cat(foods):
    print("Number of foods: ", len(foods), "\n")
    food_by_cat = {}
    for f in foods:
        cat = f["foodCategory"]["description"]
        if cat not in food_by_cat:
            food_by_cat[cat] = []
        food_by_cat[cat].append(f["description"])
    food_by_cat = {k: sorted(v) for k, v in food_by_cat.items()}
    return food_by_cat


def names_to_yaml():
    foods = load_foods()
    foods_by_cat = get_foods_by_cat(foods)
    with open(food_data_dir / "food_names.yaml", "w") as outfile:
        yaml.dump(foods_by_cat, outfile)


if __name__ == "__main__":
    names_to_yaml()
