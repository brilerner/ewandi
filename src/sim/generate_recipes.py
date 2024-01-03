
import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')


from openai import OpenAI
from utils.io import load_text_from_file, load_json, load_yaml
from utils.dates import convert_datetime, calculate_end_time, extract_date
from llm.chat import chat_completion_request, Conversation
import utils.keys as keys
from pathlib import Path
import json
import prompts.bio as PROMPTS
import yaml
from random import random

MODEL = 'gpt-4-1106-preview'
# MODEL = "gpt-3.5-turbo-1106" # this is faster!

# Set up OpenAI API key
# openai.api_key = keys.OPENAI
client = OpenAI()
root = Path('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')




def get_food_prompt(food_prefs, food_descriptions, meal_info='lunch', ingredients=None):
    system_prompt = f"""Here are is a person's general food preferences:
{food_prefs}
Your job is to construct a {meal_info} recipe for this person. The recipe should be a list of ingredients and their amounts.You can use the following ingredients:
------------------
{food_descriptions}
------------------  
"""
    
    if ingredients:
        system_prompt += f"""You must use the following ingredients: {ingredients}
"""

    system_prompt += """In the form of a JSON, return the recipe name "recipe_name" and the ingredients "ingredients" as a list containing dictionaries with the keys "name" and "grams". The "grams" is the estimated grams used in the recipe. Make sure to use the ingredient string in the list above when outputting the JSON."""

    return system_prompt

def generate_recipe(food_prefs, foods, meal_info='lunch', ingredients=None):

    food_descriptions = [food['description'] for food in foods]


    system_prompt = get_food_prompt(food_prefs, food_descriptions, meal_info=meal_info, ingredients=ingredients)
    # print(system_prompt)
    # Await information from the user on their desired meal.

    # print(prompt)
    # recipe =  get_completion(prompt, MODEL, response_format={'type':'json_object'})

    conversation = Conversation(first_message = ("system", system_prompt))
    # conversation.add_message("user", meal_info)
    response = chat_completion_request(conversation, model=MODEL, response_format={'type':'json_object'}, stream=False, temperature=0.5)
    recipe = response.choices[0].message.content 

    return recipe

def get_ingredients_to_use(diet_info, meal_type):
    use_ingredients = []
    for ingredient in diet_info:
        if meal_type in ingredient['meals']:
            prob = ingredient.get('probability', 1)
            if random() < prob:
                use_ingredients.append(ingredient['name'])
    return use_ingredients

def generate_recipes(profile='llm_v0', n_days=1, only_lunch=True):


    # get food_prefs
    food_prefs = getattr(PROMPTS, 'food_prefs')

    # food path
    food_path = root.parent /'data'/'sim' / 'food' / 'foods.json' 

    # set up directories
    profile_dir = root.parent /'data'/'sim' / 'profiles'/profile


    # Create a directory for the journal entries
    out_dir = profile_dir / 'outputs' / 'final'
    out_dir.mkdir(parents=True, exist_ok=True)


    #  get food info
    foods = load_json(food_path)

    # get meal types
    if only_lunch:
        meal_types = ['lunch']
    else:
        meals_path = profile_dir / 'inputs' / 'meals.yaml'
        meals_info = load_yaml(meals_path)
        meal_types = [meal['name'].lower() for meal in meals_info]  

    # get diet info
    diet_path = profile_dir / 'inputs' / 'diet.yaml'
    diet_info = load_yaml(diet_path)

    recipes = {meal_type:[] for meal_type in meal_types}
    for i in range(n_days):
        for meal_type in meal_types:
            # use ingredients
            ingredients = get_ingredients_to_use(diet_info, meal_type)

            recipe = generate_recipe(food_prefs, foods, meal_info=meal_type, ingredients=ingredients)
            recipe = json.loads(recipe)
            # print(recipe)
            print()
            recipes[meal_type].append(recipe)

    save_dir = profile_dir / 'outputs' / 'intermediate' 
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)

    # recipes_path = save_dir / 'recipes.yaml'
    recipes_path = save_dir / 'recipes_raw.json'
    with open(recipes_path, 'w') as file:
        # yaml.dump(recipes, file, indent=4)
        json.dump(recipes, file, indent=4)


if __name__ == "__main__":
    generate_recipes(profile='llm_v1', n_days=3, only_lunch=False)
