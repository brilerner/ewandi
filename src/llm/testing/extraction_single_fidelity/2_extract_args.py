import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))


from llm.chat import Conversation, json_request
from prompts import engine, extraction
import pandas as pd
import json
import time
import yaml

# load in the trials
df = pd.read_csv(Path(__file__).parent / "input_trials_with_prompts.csv")

# load in the params
filepath = Path(__file__).parent / "input_choices.yaml"
with open(filepath) as file:
    params = yaml.load(file, Loader=yaml.FullLoader)["params"]

kwargs = {
    "model": "gpt-4-1106-preview",
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
current_date_obj = pd.to_datetime(current_date)
dr_conventions = {
    "the last year": (current_date_obj - pd.Timedelta(days=365)).strftime("%Y-%m-%d"),
    "the last month": (current_date_obj - pd.Timedelta(days=30)).strftime("%Y-%m-%d"),
    "the last week": (current_date_obj - pd.Timedelta(days=7)).strftime("%Y-%m-%d"),
    "yesterday": (current_date_obj - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
}

conventions = {
    "dr": dr_conventions,
    "tr": time_conventions,
    "d": day_conventions,
}
rev_conventions = {k: {str(y): x for x, y in v.items()} for k, v in conventions.items()}
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
            k = f"{k}_e"
            v = str(v)
            for x, y in rev_conventions.items():
                if k == x and v in y:
                    v = y[v]
            df.loc[i, k] = v
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

# make prompt the first column by using the name
# df = df[["prompt"] + [col for col in trial_df.columns if col != "prompt"]]
df.to_csv(Path(__file__).parent / "extracted_args.csv", index=False)
