import json
from pathlib import Path

path = Path("/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/Cerebra/data/sim/food/foundationDownload.json")
foods = json.load(open(path))

ENERGY_NAME = "energy" # no need for multiple types of conversions
ENERGY_UNITS = "kcal"



def check_energy_occurrences(energy_occurrences):
    # check if there are multiple values for energy or missing amounts
    if len(energy_occurrences) == 1:
        print("Not a single energy value for", food['description']) 
        return False
    else:
        return True


def get_energy_occurrences(food):

    def check_nutrient(nutrient):
        if 'Energy' in nutrient['name']:
            return True
        else:
            return False
        
    energy_occurrences = []
    for f in food['foodNutrients']:
        if check_nutrient(f['nutrient']):
            energy_occurrences.append(f)
    return energy_occurrences




suppl_foods = [
    "Oil, olive, extra virgin",
    "Butter, stick, unsalted",
    "Salt, table, iodized",
]

terms_to_remove = [
    "Restaurant",
    "added",
    "unheated",
    "frozen",
    "dried",
    "fried",
    "heated",
    "oven",



grated
pasteurized
%
"Cheese, cottage, lowfat, 2% milkfat"
"Fish, tuna, light, canned in water, drained solids"
"Restaurant, Chinese, fried rice, without meat"
"Bread, whole-wheat, commercially prepared"
"Beef, loin, top loin steak, boneless, lip-on, separable lean only, trimmed to 1/8" fat, choice, raw"

filtered_foods = []

# only care about energy for now to avoid issues with other nutrients
for food in foods["FoundationFoods"]:

    energy_occurrences = get_energy_occurrences(food)
    if not check_energy_occurrences(energy_occurrences):
        continue
    else:
        filtered_foods.append({
            "description": food["description"],
            "nutrients": [
                {
                    "name": ENERGY_NAME,
                    "unit": ENERGY_UNITS,
                    "amount": energy_occurrences[0]['amount']
                }
            ]
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