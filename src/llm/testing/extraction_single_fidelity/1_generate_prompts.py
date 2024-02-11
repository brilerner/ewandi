import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

# import prompts as pr
from prompts import single_extract_fidelity_prompt_generation as pr
from llm.chat import json_request_prompt_only
import pandas as pd
import json
import yaml

# load in the trials
df = pd.read_csv(Path(__file__).parent / "input_trials.csv")

# load in the params
filepath = Path(__file__).parent / "input_choices.yaml"
with open(filepath) as file:
    params = yaml.load(file, Loader=yaml.FullLoader)["params"]


kwargs = {
    "model": "gpt-4-1106-preview",
    "temperature": 0,
}


# make prompts for each row
col_longnames = {
    "v": "variable",
    "p": "people",
    "dr": "date_range",
    "tr": "time_range",
    "d": "days",
}



print("\nGenerating prompts for {} rows".format(len(df)))
for i, row in df.rename(columns=col_longnames).iterrows():
    # get the system prompt
    row = row.dropna()
    gp = pr.get_system(row, params["current_date"], params["current_time"])
    df.loc[i, "generation_prompt"] = gp

    # get the user prompt
    print(f"Generating prompt for row {i}")
    user_query_json = json_request_prompt_only(gp, load=False, **kwargs)
    # user_query_json = "{'test': 'test'}"
    df.loc[i, "user_query_json"] = user_query_json
    try:
        df.loc[i, "user_query"] = json.loads(user_query_json)["prompt"]
    except Exception as e:
        df.loc[i, "user_query"] = e

    inputs = "\n".join([f"- {k}: {v}" for k, v in row.items()])
    print(inputs)
    print(user_query_json)
    print()


# add the model and temp values as columns to the dataframe
for k, v in kwargs.items():
    df[k] = v

# # change the columns in col_longnames to have a "_i" suffix; there will be more columns, so just change those
# df = df.rename(columns={k: f"{k}_i" for k in col_longnames.keys()})

df = df.set_index(list(kwargs))
# make prompt the first column by using the name
# df = df[["prompt"] + [col for col in trial_df.columns if col != "prompt"]]
df.to_csv(Path(__file__).parent / "input_trials_with_prompts.csv")


#   prompt = f"""I am going to give you an input set of words/phrases, for which I would like you to generate a a set of group names that sufficiently capture the relationships between different members of the input set, where a group is a word/phrase that can be used to describe all members of the group.
# Any words/phrases in parentheses are there to add useful context. If a colon is present, the text after the colon provides further description.
# Please return the group names as a JSON, i.e. {{'groups': ['group1', 'group2', 'group3', '...']}}.
# For example:
# - if the input set contains 'basketball game' and 'basketball practice', 'basketball activities' would be a good group name.
# - if the input set contains 'basketball game' and 'soccer game', 'sports' would be a good group name.
# - if the input set contains 'reading' and 'watching TV', 'leisure activities' would be a good group name.
# Here is the input set, where each row denotes a separate word/phrase:
# {input_string}

# Go!
# """
#
