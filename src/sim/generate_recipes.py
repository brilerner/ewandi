import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

import copy
import json
import random
from pathlib import Path

from llm.chat import json_request
from prompts.recipes import get_food_prompt
from utils.io import load_yaml
from utils.sampling import get_sample

MODEL = "gpt-4-1106-preview"
# MODEL = "gpt-3.5-turbo-1106"  # this is faster!


def prepare_ingredients(foods, diet_info, meal_type):
    def get_ingredients_to_use(diet_info, meal_type):
        use_ingredients = {}
        for ingredient in diet_info:
            if meal_type in ingredient["meals"]:
                prob = ingredient.get("probability", 1)
                if random.random() < prob:
                    use_ingredients[ingredient["name"]] = True
                else:
                    use_ingredients[ingredient["name"]] = False
        return use_ingredients

    def remove_foods(foods, remove_foods):
        for cat, cat_foods in foods.items():
            foods[cat] = [f for f in cat_foods if f not in remove_foods]
        return foods

    foods = copy.deepcopy(foods)

    special_ingredients_dict = get_ingredients_to_use(diet_info, meal_type)
    must_use_ingredients = [
        f for f in special_ingredients_dict if special_ingredients_dict[f]
    ]
    ingredients_to_remove = [
        f for f in special_ingredients_dict if not special_ingredients_dict[f]
    ]
    foods_by_cat = remove_foods(foods, ingredients_to_remove)
    all_foods = [f for cat in foods_by_cat.values() for f in cat]

    return {"all": all_foods, "by_cat": foods_by_cat, "must_use": must_use_ingredients}


def sample_calories(healthiness):
    if healthiness == "high":
        return random.randint(200, 400)
    elif healthiness == "medium":
        return random.randint(400, 600)
    elif healthiness == "low":
        return random.randint(600, 800)


def validate_recipe(recipe, ingredient_usage):
    # validate args
    if "ingredients" not in recipe:
        raise Exception("No ingredients in recipe")
    if not isinstance(recipe["ingredients"], list):
        raise Exception("Ingredients not a list")
    if "name" not in recipe:
        raise Exception("No name in recipe")
    if not isinstance(recipe["name"], str):
        raise Exception("Name not a string")
    # if "calories" not in recipe:
    #     raise Exception("No calories in recipe")
    # if not isinstance(recipe["calories"], str):
    #     raise Exception("Calories not a str")
    # if recipe["calories"] not in ["low", "medium", "high"]:
    #     raise Exception("Calories not low, medium, or high")

    # validate ingredients
    unknown_ingredients = [
        ingredient
        for ingredient in recipe["ingredients"]
        if ingredient not in ingredient_usage["all"]
    ]
    missing_ingredients = [
        ingredient
        for ingredient in ingredient_usage["must_use"]
        if ingredient not in recipe["ingredients"]
    ]

    if unknown_ingredients:
        print("INGREDIENT NOT FOUND:", unknown_ingredients)
        raise Exception("Ingredient not found")
    if missing_ingredients:
        print("INGREDIENT NOT USED:", missing_ingredients)
        raise Exception("Must use ingredient not in recipe")


def save_recipe(recipe, meal_type, save_path):
    if save_path.exists():
        with open(save_path, "r") as file:
            recipes = json.load(file)

        if not isinstance(recipes, dict):
            raise Exception("Recipes not a dict")
        if meal_type not in recipes:
            recipes[meal_type] = []
    else:
        recipes = {meal_type: []}

    # add new recipe
    recipes[meal_type].append(recipe)
    with open(save_path, "w") as file:
        json.dump(recipes, file, indent=4)


def resave_recipes(recipes_save_path):
    if recipes_save_path.exists():
        with open(recipes_save_path, "r") as file:
            recipes = json.load(file)
        from datetime import datetime

        new_path = (
            recipes_save_path.parent / f"recipes_resaved_at_{datetime.now()}.json"
        )
        with open(new_path, "w") as file:
            json.dump(recipes, file, indent=4)
        # now delete old
        recipes_save_path.unlink()


def generate_recipe(meal_type, ingredient_usage, healthiness="medium"):
    system_prompt = get_food_prompt(meal_type, ingredient_usage, healthiness)
    # print(system_prompt)
    recipe = json_request(system_prompt, temperature=1.5, model=MODEL)

    return recipe


def generate_recipes(
    profile="llm_v0",
    n_days=1,
    input_meal_type=None,
):
    # set up directories
    sim_data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "sim"

    profile_dir = sim_data_dir / "profiles" / profile

    food_path = sim_data_dir / "foods" / "food_names_manual.yaml"

    diet_path = profile_dir / "inputs" / "constructors" / "diet.yaml"

    meals_path = profile_dir / "inputs" / "events" / "meals.yaml"

    save_dir = profile_dir / "outputs" / "intermediate"
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)

    recipes_save_path = save_dir / "recipes.json"
    resave_recipes(recipes_save_path)

    #  get foods and diet info
    foods = load_yaml(food_path)
    diet_info = load_yaml(diet_path)
    ingredient_prefs = diet_info["ingredients"]
    health = diet_info["health_values"]
    meals_info = load_yaml(meals_path)

    # get meal types
    if input_meal_type:
        meal_types = [input_meal_type.lower()]
    else:
        meal_types = [meal["name"].lower() for meal in meals_info]

    for i in range(n_days):
        for meal_type in meal_types:
            healthiness = get_sample(health["vals"], health["probs"])
            calories = sample_calories(healthiness)
            ingredient_usage = prepare_ingredients(foods, ingredient_prefs, meal_type)
            try_limit = 50
            try_count = 0
            while try_count < try_limit:
                try:
                    print(
                        f"DAY: {i+1}  MEAL: {meal_type}  TRY: {try_count}  HEALTH: {healthiness} MUST_USE: {ingredient_usage["must_use"]}"
                    )

                    recipe = generate_recipe(meal_type, ingredient_usage, healthiness)
                    validate_recipe(recipe, ingredient_usage)
                    recipe["ingredients"] = [i.lower() for i in recipe["ingredients"]]
                    recipe["calories"] = calories

                    print("RECIPE NAME: ", recipe["name"])
                    print("RECIPE INGREDIENTS: ", recipe["ingredients"])
                    print("RECIPE CALORIES: ", recipe["calories"])
                    print()

                    save_recipe(recipe, meal_type, recipes_save_path)

                    break
                except Exception as e:
                    print("ERROR: ", e)
                    print("Retrying...")
                    print()
                    try_count += 1
                    if try_count == try_limit:
                        raise Exception("Could not generate recipe")
                    continue


if __name__ == "__main__":
    generate_recipes(profile="llm_v1", n_days=20)  # , input_meal_type="lunch")
