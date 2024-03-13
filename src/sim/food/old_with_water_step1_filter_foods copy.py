import json
from pathlib import Path

path = Path("/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/Cerebra/data/sim/food/foundationDownload.json")
foods = json.load(open(path))


add_foods = [
    "Water"
]

suppl_foods = [
    "Water",
    "Oil, olive, extra virgin",
    "Butter, stick, unsalted",
    "Salt, table, iodized",
]

filtered_foods = []

# add user-created foods
for food in add_foods:
    filtered_foods.append({
        "description": food,
        "nutrients": []
    })

# add calories 
for food in foods["FoundationFoods"]:

    # energy = [f['nutrient'] for f in food['foodNutrients'] if 'Energy' in f['nutrient']['name']]
    # amount = [f['amount'] for f in food['foodNutrients'] if 'Energy' in f['nutrient']['name']]

    energy_name = "energy" # no need for multiple types of conversions
    unit_name = "kcal"

    # check if there are multiple values for energy or missing amounts
    energy_occurrences = []
    for f in food['foodNutrients']:
        if 'Energy' not in f['nutrient']['name']:
            continue
        elif 'amount' not in f:
            continue
        else:
            energy_occurrences.append(f)
    # only take first energy value if more than two
    if len(energy_occurrences)>=2:
        print("More than one energy value for", food['description']) # fix later?
        energy_occurrences = energy_occurrences[:2]


    # deal with supplementary
    nutrients_dict_list = []
    if len(energy_occurrences) == 0:
        # remove food if not in suppl_foods
        if food['description'] not in suppl_foods:
            print("No energy value for", food['description'])
            continue
        else:
            pass
    else:
        nutrients_dict_list.append({
            'name' : energy_name, # just in case there are variations in energy phrasing
            'unit' : unit_name,
            'amount' : energy_occurrences[0]['amount']
        })
    # append
    filtered_foods.append({
        "description": food["description"],
        "nutrients": nutrients_dict_list
    })


for food in filtered_foods:
    if food['description'] in suppl_foods:
        food['is_supplement'] = True
    else:
        pass
        # food['is_supplement'] = False
    
save_path = path.parent / "foods.json"
with open(save_path, 'w') as f:
    json.dump(filtered_foods, f, indent=4)