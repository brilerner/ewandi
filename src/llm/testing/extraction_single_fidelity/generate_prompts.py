import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

# import prompts as pr
from prompts import single_extract_fidelity_prompt_generation as pr
from llm.chat import json_request_prompt_only
import pandas as pd
import json
import yaml


# load in the params
def generate_prompts(name="simple", temperature=1.5):
    filepath = Path(__file__).parent / f"input_choices_{name}.yaml"
    with open(filepath) as file:
        params = yaml.load(file, Loader=yaml.FullLoader)["params"]

    # load in the trials
    df = pd.read_csv(Path(__file__).parent / f"input_trials_{name}.csv")



    kwargs = {
        "model": "gpt-4-1106-preview",
        "temperature": temperature,
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
    df.to_csv(Path(__file__).parent / f"input_trials_with_prompts_{name}.csv")

if __name__ == "__main__":
    profile = "llm_v1"
    generate_prompts(name=profile)