import json
from pathlib import Path

path = Path("/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/Cerebra/data/sim/examples/food/foundationDownload.json")
foods = json.load(open(path))


filtered_foods = []
for food in foods["FoundationFoods"]:
    energy = [f['nutrient'] for f in food['foodNutrients'] if 'Energy' in f['nutrient']['name']]
    amount = [f['amount'] for f in food['foodNutrients'] if 'Energy' in f['nutrient']['name']]

    energy_name = "energy" # no need for multiple types of conversions
    unit_name = "kcal"

    nutrients_dict = {"name": "energy", "unit": "kcal"}
    if len(energy) == 0:
        print("No energy value for", food['description'])
        nutrients_dict = {}
    if len(energy) > 0:
        if len(energy) > 1:
            print("More than one energy value for", food['description'])
        nutrients_dict['amount'] = amount[0]
        
    filtered_foods.append({
        "description": food["description"],
        "nutrients": [ 
            nutrients_dict
        ]
    })
    
save_path = path.parent / "foods.json"
with open(save_path, 'w') as f:
    json.dump(filtered_foods, f, indent=4)