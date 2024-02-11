import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

import random
import yaml
import pandas as pd

# load in the list of potential input choices
filepath = Path(__file__).parent / "input_choices.yaml"
with open(filepath) as file:
    all_data = yaml.load(file, Loader=yaml.FullLoader)
    input_choices = all_data["data"]
    params = all_data["params"]

n_input_trials = 10
inclusion_prob = 0.5

trial_data = []

for i in range(n_input_trials):
    inputs = {}
    for input_type in input_choices:
        if (random.random() < inclusion_prob) or input_type == "v":
            inputs[input_type] = random.choice(input_choices[input_type])
    trial_data.append(inputs)

for trial in trial_data:
    # only include days if date range is greater than 1 month
    if "dr" in trial and "d" in trial:
        # this is just supposed to simplify things for now
        if not any([x in trial["dr"] for x in ["year", "month"]]):
            trial.pop("d", None)
        # start, end = trial["dr"].split("--")
        # start = pd.to_datetime(start)
        # if end == "":
        #     end = pd.to_datetime(params["current_date"])
        # else:
        #     end = pd.to_datetime(end)
        # if (end - start).days < 30:
        #     trial.pop("d", None)

df = pd.DataFrame(trial_data)
df.to_csv(Path(__file__).parent / "input_trials.csv", index=False)
