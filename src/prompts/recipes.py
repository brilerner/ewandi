def get_food_prompt(meal_type, ingredient_usage, healthiness="medium"):
    def convert_foods_to_string(foods):
        foods_str = ""
        for category, foods in foods.items():
            foods_str += f"{category}:\n"
            for food in foods:
                foods_str += f"  - {food}\n"
        return foods_str

    all_ingredients_string = convert_foods_to_string(ingredient_usage["by_cat"])
    must_use_ingredients_string = ", ".join(ingredient_usage["must_use"])

    system_prompt = f"""You are a chef who creates recipes for people with different dietary needs. You are creating a {meal_type} recipe. The healthiness of this meal should be {healthiness}. 
Here is a list of ingredients you can use, listed by category:
{all_ingredients_string}
Please adhere to the following guidelines:
- You may use only ingredients in this list.
"""
    if must_use_ingredients_string:
        system_prompt += f"""-You MUST use the following ingredients: {must_use_ingredients_string}\n"""

    system_prompt += """Please return a JSON containing a name for the recipe, and a list of ingredients used. When constructing the recipe name, avoid using unneeded adjectives such as "healthy" or "decadent"; just keep it simple. While a recipe may call for a specific preparation or type of an ingredient, when listing the ingredients used in the output JSON, please phrase ingredient names phrased exactly as shown above. The JSON must be formatted with keys "name" and "ingredients". Return the ingredient names exactly as they are listed above. I repeat, exactly.
Go!"""

    return system_prompt


# - Of these ingredients, you may incorporate different preparations or subcategories into the recipe. Here are a few examples along these lines:
#     - beef --> steak for
#     - tomatoes--> grape tomatoes
#     - bread --> bun
#     - lemons --> lemon juice
# def get_food_prompt(
#     food_prefs, food_names_string, meal_info="lunch", must_use_ingredients=None
# ):
#     must_use_ingredients_string = ", ".join(must_use_ingredients)

#     system_prompt = f"""Here are a person's general food preferences:
# {food_prefs}
# Your job is to construct a {meal_info} meal for this person from a list of given ingredients, and only this list of ingredients.
# You may use any of the following ingredients, listed by category:
# {food_names_string}
# """
#     if must_use_ingredients:
#         system_prompt += f"""While you may use any of the listed ingredients, you MUST use the following ingredients: {must_use_ingredients_string}\n"""

#     system_prompt += """Also, DO NOT use any ingredients that are not listed above.
#     In addition to the ingredients, please prove a name for the recipe, and estimate whether the meal has a low, medium, or high number of calories.
#     Return the recipe in the form of a JSON, where the keys are "name" (value --> recipe name), "ingredients" (value --> list of ingredients), and "calories" (value --> low, medium, or high).
#     Make sure to return the ingredient names EXACTLY as they are listed above. I repeat, exactly.
#     """

#     return system_prompt
