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


def generate_food_names(profile="llm_v1"):
    # food path
    food_dir = root.parent / "data" / "sim" / "food"
    food_path = food_dir / "foods.json"
    #  get food info
    foods = load_json(food_path)

    # foods = foods[:]

    for f in foods:
        # get food name
        food_name = lowercase_first_letter(f["description"])

        # get food name prompt
        food_name_prompt = prompt

        # get completion
        conversation = Conversation(first_message=food_name_prompt)

        conversation.add_message("user", food_name)

        response = chat_completion_request(
            conversation,
            model=MODEL,
            stream=False,
            resubmit=False,
            append=False,
            response_format={"type": "json_object"},
        )

        # get completion text
        try:
            completion_text = response.choices[0].message.content

            # do something to deal with the percent issue
            # ....

            # convert json
            breakdown = json.loads(completion_text)
            print()
            print("FOOD_NAME: ", food_name)
            print(f"BREAKDOWN: {breakdown}")
            print()

            f["name"] = breakdown["core_name"]
            f["subtypes"] = breakdown["subtypes"]
            f["preparations"] = breakdown["preparations"]

        except:
            print("ERROR: ", food_name)
            continue

    save_path = food_dir / "foods_revised.json"
    with open(save_path, "w") as file:
        json.dump(foods, file, indent=4)


if __name__ == "__main__":
    generate_food_names(profile="llm_v1")
