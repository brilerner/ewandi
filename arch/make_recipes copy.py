
import sys
sys.path.append('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')


from openai import OpenAI
from utils.io import load_text_from_file, load_json
from utils.dates import convert_datetime, calculate_end_time, extract_date
from llm.chat import chat_completion_request, Conversation
import utils.keys as keys
from pathlib import Path
import json
import prompts.bio as PROMPTS

MODEL = 'gpt-4-1106-preview'
# MODEL = "gpt-3.5-turbo-1106" # this is faster!

# Set up OpenAI API key
# openai.api_key = keys.OPENAI
client = OpenAI()
root = Path('/Users/brianlerner/Library/CloudStorage/OneDrive-Personal/Code/cerebra/src')





def make_recipe(food_prefs, foods, meal_info='lunch'):
    food_descriptions = [food['description'] for food in foods]

    system_prompt = f"""Here are is a person's general food preferences:
{food_prefs}
Your job is to construct a {meal_info} recipe for this person. The recipe should be a list of ingredients and their amounts.You can use the following ingredients:
------------------
{food_descriptions}
------------------  
In the form of a JSON, return the recipe name "recipe_name" and the ingredients "ingredients" as a list containing dictionaries with the keys "name" and "grams". The "grams" is the estimated grams used in the recipe. Make sure to use the ingredient string in the list above when outputting the JSON.
"""
# Await information from the user on their desired meal.

    # print(prompt)
    # recipe =  get_completion(prompt, MODEL, response_format={'type':'json_object'})

    conversation = Conversation(first_message = ("system", system_prompt))
    # conversation.add_message("user", meal_info)
    response = chat_completion_request(conversation, model=MODEL, response_format={'type':'json_object'}, stream=False, temperature=0.5)
    recipe = response.choices[0].message.content 

    return recipe

def make_recipes(profile='llm_v0', n_days=1, all_meals=False):


    # get food_prefs
    food_prefs = getattr(PROMPTS, 'food_prefs')

    # food path
    food_path = root.parent /'data'/'sim' / 'food' / 'foods.json'    
    # set up directories
    profile_dir = root.parent /'data'/'sim' / 'profiles'/profile


    # Create a directory for the journal entries
    out_dir = profile_dir / 'outputs' / 'final'
    out_dir.mkdir(parents=True, exist_ok=True)


    # Process each file
    # process_files(food_prefs, food_path, out_dir)
    foods = load_json(food_path)

    recipes = []
    for i in range(n_days):
        if all_meals:
            meal_types = ['breakfast', 'lunch', 'dinner']
        else:
            meal_types = ['lunch']
        meals = {meal_type:[] for meal_type in meal_types}
        for meal_type in meals:
            recipe = make_recipe(food_prefs,foods, meal_info=meal_type)
            recipe = json.loads(recipe)
            print(recipe)
            print()
            meals[meal_type].append(recipe)
            recipes.append(recipe)

    save_dir = profile_dir / 'outputs' / 'intermediate' 
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)

    recipes_path = save_dir / 'recipes_raw.json'
    with open(recipes_path, 'w') as file:
        json.dump(recipes, file, indent=4)


if __name__ == "__main__":
    make_recipes(profile='llm_v0', n_days=2, all_meals=True)
