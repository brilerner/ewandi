import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src":
    src_dir = src_dir.parent
sys.path.append(str(src_dir))


import yaml
import pandas as pd
import json
import shutil


def load_yaml(path):
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    return data


def load_input_yaml(profile="llm_v0"):
    root_dir = "/Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/Code/Ewandi/data/sim/profiles"
    inputs_dir = Path(root_dir) / profile / "inputs"
    # set up directories
    # inputs_dir = Path.cwd().parent /'data'/'sim' / 'profiles'/profile/'inputs'
    sim_params_path = inputs_dir / "sim_params.yaml"
    calendar_events_path = inputs_dir / "calendar_events.yaml"
    sensations_path = inputs_dir / "sensations.yaml"
    hobbies_path = inputs_dir / "hobbies.yaml"

    # Load the YAML files
    with open(sim_params_path, "r") as file:
        sim_params = yaml.safe_load(file)

    with open(calendar_events_path, "r") as file:
        calendar_events = yaml.safe_load(file)

    with open(sensations_path, "r") as file:
        sensations = yaml.safe_load(file)

    with open(hobbies_path, "r") as file:
        hobbies = yaml.safe_load(file)

    return sim_params, calendar_events, sensations, hobbies


# Function to load text from a file
def load_text_from_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def load_csv_file(file_path):
    """
    Load a CSV file and return its content.

    Args:
    file_path (str): Path to the CSV file.

    Returns:
    DataFrame: Content of the CSV file.
    """
    return pd.read_csv(file_path)


def load_json(file_path):
    """
    Load a JSON template file and return its content.

    Args:
    file_path (str): Path to the JSON file.

    Returns:
    dict: Content of the JSON file.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def load_yaml_file(file_path):
    """
    Load a YAML file and return its content.

    Args:
    file_path (str): Path to the YAML file.

    Returns:
    dict: Content of the YAML file.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


#### SAVE


def save_jsons_to_directory(events_jsons, save_dir, filename):
    """
    Save a list of JSONs to a specified directory.

    Args:
    events_jsons (list): List of calendar event JSONs.
    directory_name (str): Name of the directory to save files.
    """
    if not Path(save_dir).exists():
        Path(save_dir).mkdir(parents=True, exist_ok=True)
    save_path = save_dir / filename
    with open(save_path, "w") as file:
        json.dump(events_jsons, file, indent=4)


def delete_directory_contents(directory_path):
    # Iterate over each item in the directory
    for item in Path(directory_path).iterdir():
        if item.is_dir():
            # If it's a directory, delete it and all its contents
            shutil.rmtree(item)
        else:
            # If it's a file, delete it
            item.unlink()
