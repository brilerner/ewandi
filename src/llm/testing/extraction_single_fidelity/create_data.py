import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

import random
import yaml
import pandas as pd
import numpy as np
from server.retrieve import get_elements, get_embeddings

def load_names_from_server(profile, n=5, method='embeddings'):

    if method == 'elements':

        def get_names(elements, s, category=None):
            names = []
            for e in elements.values():
                if category is None or e['category'] == category:
                    names.append(e['name'])
            return list(np.random.choice(
                    names,
                    size=s,
                    replace=False
                ))

        elements = get_elements(profile=profile)
        # get the event names
        event_names = get_names(elements['events']['core'], n, category='activity')
        # hack for now
        event_names =[e+" (activity)" for e in event_names]

        # sample the group size for relations
        group_size = np.random.choice(
            [1, 2, 3], 
            p=[0.5, 0.3, 0.2],
            size=n
            )
        relation_names = []
        for gs in group_size:
            relation_names.append(
                get_names(elements['relations']['core'], gs)
        )

    elif method == 'embeddings':
        emb_dict = get_embeddings(profile='llm_v1')

        all_events = [v['base'] for v in emb_dict['events'] if v['partition'] == 'core']
        all_relations = [v['base'] for v in emb_dict['relations'] if v['partition'] == 'core']
        event_names =   list(np.random.choice(
                            all_events,
                            size=n,
                            replace=True
                        ))
        
        # sample the group size for relations
        group_size = np.random.choice(
            [1, 2, 3], 
            p=[0.5, 0.3, 0.2],
            size=n,
            replace=True
            )
        relation_names = []
        for gs in group_size:
            relation_names.append(
                list(np.random.choice(
                            all_relations,
                            size=gs,
                            replace=False
                        )))
        
    return event_names, relation_names

def create_data(name="simple", n_input_trials=2, inclusion_prob=0.5):
    # load in the list of potential input choices
    filepath = Path(__file__).parent / f"input_choices_{name}.yaml"
    with open(filepath) as file:
        all_data = yaml.load(file, Loader=yaml.FullLoader)
        input_choices = all_data["data"]
        params = all_data["params"]
        name = all_data["name"]


    if load_info := all_data.get("load"):
        event_names, relation_names = load_names_from_server(name, n_input_trials)
        input_choices["v"] = event_names
        input_choices["p"] = relation_names

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
    df = df[["v", "p", "dr", "tr", "d"]]
    df.to_csv(Path(__file__).parent / f"input_trials_{name}.csv", index=False)

if __name__ == "__main__":
    profile = "llm_v1"
    n = 5
    create_data(name=profile, n_input_trials=n)