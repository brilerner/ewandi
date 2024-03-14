import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src":
    src_dir = src_dir.parent
sys.path.append(str(src_dir))


from openai import OpenAI
from utils.general import lowercase_first_letter
from utils.io import load_text_from_file, load_json, load_yaml
from utils.dates import convert_datetime, calculate_end_time, extract_date
from llm.chat import chat_completion_request, Conversation
import utils.keys as keys
from pathlib import Path
import json
import prompts.bio as PROMPTS
import yaml
from random import random

from collections import defaultdict

MODEL = "gpt-4-1106-preview"
# MODEL = "gpt-3.5-turbo-1106" # this is faster!

# Set up OpenAI API key
# openai.api_key = keys.OPENAI
client = OpenAI()
root = Path(
    "/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/ewandi/src"
)


prompt = """I will give you a description of a food, including information on the core food and potentially, its preparations.
Please break the description down into the core food, it's subtypes, and its preparations as a JSON, with keys 'core_name', 'subtypes', and 'preparations' respectively. 
If no preparations are needed, please leave the 'preparations' value as an empty list.
If no subtypes are needed, please leave the 'subtypes' value as an empty list.
In this JSON, 'core_name' should be a string, 'subtypes' should be a list of strings, and 'preparations' should be a list of strings.
Ignore non-specific phrases that have no impact on the nutritional content of an input ingredient, such as but not limited to "restaurant" or "refrigerated".
Ignore phrases describing broad food-groups, such as "melons" for "cantaloupe".
Here are a few examples to guide your process:

Input: "flour, whole wheat, unenriched"
Output: {"core_name": "flour", "subtypes":["whole_wheat"], "preparations": ["unenriched"]}

Input: "yogurt, Greek, plain, whole milk"
Output: {"core_name": "yogurt", "subtypes":["Greek"] "preparations": ["plain", "whole milk"]}

Input: "buttermilk, low fat"
Output: {"core_name": "buttermilk", "subtypes":[], "preparations": ["low fat"]}

Input: "orange juice, no pulp, not fortified, not from concentrate, refrigerated"
Output: {"core_name": "orange juice", "subtypes":[], "preparations": ["not fortified", "no pulp", "not from concentrate"]}

Input: "melons, cantaloupe, raw"
Output: {"core_name": "cantaloupe", "subtypes":[], "preparations": ["raw"]}

Input: ""oil, olive, extra virgin""
Output: {"core_name": "olive oil", "subtypes":[], "preparations": ["extra virgin"]}

Input: ""water""
Output: {"core_name": "water", "subtypes":[], "preparations": []}

Now, await the input.
"""


def reduce_foods():
    # food path
    food_dir = root.parent / "data" / "sim" / "food"
    food_path = food_dir / "foods_revised.json"
    #  get food info
    foods = load_json(food_path)

    # foods = foods[:]

    food_dict = defaultdict(list)
    for f in foods:
        food_dict[f["name"]].append(f)

    reduced_food_list = []
    for k, v in food_dict.items():
        if len(v) == 1:
            print("Length greater than 1")
            print(k)
            print(v)
        reduced_food_list.append(v[0])

    save_path = food_dir / "foods_revised_reduced.json"
    with open(save_path, "w") as file:
        json.dump(reduced_food_list, file, indent=4)


if __name__ == "__main__":
    reduce_foods()
