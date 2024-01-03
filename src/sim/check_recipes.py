
import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')


from openai import OpenAI
from utils.io import load_text_from_file, load_json
from utils.dates import convert_datetime, calculate_end_time, extract_date
import utils.keys as keys
from pathlib import Path
import json
import prompts.bio as PROMPTS


root = Path('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')


amount_conversion_factor = 1/100

def check_recipe(recipe, foods):

    foods = [f['description'] for f in foods]

    for ingredient in recipe["ingredients"]:
        if ingredient['name'] not in foods:
            pass
            # print("INGREDIENT NOT FOUND")
            # print(recipe['recipe_name'])
            # print(ingredient['name'])   
            # print()

def add_nutrients(recipe, foods):

    recipe_ingredients = recipe['ingredients']
    total_kcal = 0
    for ingredient in recipe_ingredients:

        print(ingredient)
        food_nutrients = [f['nutrients'] for f in foods if f['description'] == ingredient['name']]
        if len(food_nutrients) != 1:
            continue
        else:
            food_nutrients  = food_nutrients[0]
        print(food_nutrients)
    
        nutrient_list = []
        for nutrient in food_nutrients:
            if 'amount' in nutrient:
                nutrient['amount_per_100g'] = nutrient['amount']
                del nutrient['amount']
            else:
                print("Not found:", nutrient)
                continue
            if nutrient["name"] == "energy":
                adjusted_amount = nutrient['amount_per_100g'] * ingredient['grams']*amount_conversion_factor
                nutrient['amount'] = adjusted_amount
                total_kcal += adjusted_amount
            nutrient_list.append(nutrient)
        ingredient['nutrients'] = nutrient_list
            # print('RECIPE', recipe)

    recipe['kcal'] = total_kcal



def check_recipes(profile='llm_v0'):

    # food path
    food_path = root.parent /'data'/'sim' / 'food' / 'foods.json'    
    foods = load_json(food_path)
    
    # set up directories
    profile_dir = root.parent /'data'/'sim' / 'profiles'/profile

    recipes_path = profile_dir / 'outputs' / 'intermediate' / 'recipes_raw.json'
    if recipes_path.exists():
        recipes = load_json(recipes_path)
    else:
        raise Exception("No recipes found")

    print()
    for meal_type in recipes:
        print(meal_type)
        print()
        # for i in range(len(recipes[meal_type])):
        for recipe in recipes[meal_type]:
            # print(recipes[meal_type][i])
            # print()
            
            # print out any missing ingredients
            # check_recipe(recipes[meal_type][i], foods)
            check_recipe(recipe, foods)

            # add nutrients where they exist
            # add_nutrients(recipes[meal_type][i], foods)
            add_nutrients(recipe, foods)

    # print(recipes) 
    # recipes_path = profile_dir / 'outputs' / 'intermediate' / 'recipes_final.json'
    recipes_path = profile_dir / 'outputs' / 'intermediate' / 'recipes_final.json'
    with open(recipes_path, 'w') as file:
        json.dump(recipes, file, indent=4)


if __name__ == "__main__":
    check_recipes(profile='llm_v1')
