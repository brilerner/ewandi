import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))


from llm.chat import Conversation, json_request
from prompts import engine, extraction
import pandas as pd
import json
import time
import yaml
import numpy as np

def extract_args(name="simple", n=None, model="gpt-4-1106-preview"):
    # load in the trials
    df = pd.read_csv(Path(__file__).parent / f"input_trials_with_prompts_{name}.csv")
    if n:
        df = df.head(n)

    # load in the params
    filepath = Path(__file__).parent / f"input_choices_{name}.yaml"
    with open(filepath) as file:
        params = yaml.load(file, Loader=yaml.FullLoader)["params"]

    kwargs = {
        "model": model,
        "temperature": 0,
    }
    # add the model and temp values as columns to the dataframe
    for k, v in kwargs.items():
        df[k] = v

    # df = df.set_index(list(kwargs))

    # # change the columns in col_longnames to have a "_i" suffix; there will be more columns, so just change those
    col_mapping = {k: f"{k}_i" for k in ["v", "p", "dr", "tr", "d"]}
    df = df.rename(columns=col_mapping)

    time_conventions = {
        "morning": "06:00--12:00",
        "afternoon": "12:00--18:00",
        "night": "18:00--00:00",
    }

    # "WD" for weekdays, "WE" for weekends.
    day_conventions = {
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "weekend": ["Sat", "Sun"],
    }

    current_date = params["current_date"]
    current_time = params["current_time"]
    # convert date to datetime object


    def convert_dr_convention(current_date, days):
        current_date_obj = pd.to_datetime(current_date)
        start = (current_date_obj - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
        end = current_date_obj.strftime("%Y-%m-%d")
        return f"{start}--{end}"


    dr_conventions = {
        "the last year": convert_dr_convention(current_date, 365),
        "the last month": convert_dr_convention(current_date, 30),
        "the last week": convert_dr_convention(current_date, 7),
        "yesterday": convert_dr_convention(current_date, 1),
    }

    conventions = {
        "dr": dr_conventions,
        "tr": time_conventions,
        "d": day_conventions,
    }
    rev_conventions = {k: {str(y): x for x, y in v.items()} for k, v in conventions.items()}
    # rev_conventions = {k: {str(y): x for x, y in v.items()} for k, v in conventions.items()}
    # now write the same but in reverse hardcoded; actually write the whole thing


    extraction_system_prompt = extraction.get_system(
        conventions, current_date, current_time
    )
    # print(extraction_system_prompt)
    print("\nExtracting args for {} rows".format(len(df)))
    for i, row in df.iterrows():
        print(f"Extracting args for row {i}")
        query = row["user_query"]

        # set up conversation
        conv = Conversation()
        conv.add_text_message("system", engine.system)
        conv.add_text_message("system", extraction_system_prompt)
        conv.add_text_message("user", query)
        df.loc[i, "prompt"] = str(conv.messages)

        start_time = time.time()
        args_json = json_request(conv.messages, load=False, **kwargs)
        df.loc[i, "request_time_s"] = round(time.time() - start_time, 2)

        df.loc[i, "args_json"] = args_json
        try:
            args = json.loads(args_json)
            df.loc[i, "args"] = str(args)
            for k, v in args.items():
                v = str(v)
                for x, y in rev_conventions.items():
                    if k == x and v in y:
                        v = y[v]
                k = f"{k}_e"
                df.loc[i, k] = str(v)
        except Exception as e:
            df.loc[i, "args"] = e
            raise

    # reorder columns so that the each set of columns is together; i.e. "v_i" with "v_e", "p_i" with "p_e", etc.
    # cols = sorted([c for c in df.columns if c.endswith("_i") or c.endswith("_e")])
    for k in col_mapping.keys():
        for t in ["i", "e"]:
            col = f"{k}_{t}"
            if col not in df.columns:
                df[col] = None

    cols = list(kwargs.keys())
    cols += [f"{c}_{t}" for c in ["v", "p", "dr", "tr", "d"] for t in ["i", "e"]]
    cols += ["request_time_s", "prompt", "user_query", "args_json", "args"]
    df = df[cols]

    df = df.replace([np.nan], [None])
    df = df.replace(["nan"], [None])  # not sure where the nan is coming from

    # make prompt the first column by using the name
    # df = df[["prompt"] + [col for col in trial_df.columns if col != "prompt"]]
    df.to_csv(Path(__file__).parent / f"extracted_args_{name}.csv", index=False)

if __name__ == "__main__":
    extract_args()