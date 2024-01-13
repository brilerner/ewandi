import openai
from utils.io import load_text_from_file, load_yaml_file
from utils.dates import convert_datetime, calculate_end_time, extract_date, get_days_from_range
import utils.keys as keys
from pathlib import Path
import json
import prompts.bio as PROMPTS
from utils.hardcoded import ENTRY_PROMPT_DIVIDER


# MODEL = "gpt-4"
MODEL = "gpt-3.5-turbo-1106" # this is faster!

ENTRY_START_TIME = "23:55:00"
ENTRY_DURATION = {'minutes': 5}

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def make_entry_prompt(biography, information):
    prompt = "Please pretend that you are the person described in the following short biography:\n\n" + biography + \
    "\n\nNow, I will provide you with information regarding events that you experienced on a particular day:\n\n" + information + \
    "\n\nNow, please write a journal entry from the following perspective: " \
    "After you have wrapped up all of your activities for the day and are preparing to turn in, " \
    "describe your thoughts and emotions about the day. Be candid and concise. You do not need to" \
    "state the date at the beginning of your entry. You may begin writing now." 
    return prompt

def process_files(bio, entry_prompts, dates, entry_dir):
    entries = []  # List to store all entries
    for day_entry_prompt, date in zip(entry_prompts, dates):

        # form full prompt
        entry_prompt = make_entry_prompt(bio, day_entry_prompt)

        # get response
        response = get_completion(entry_prompt, MODEL)

        # set up date
        start_datetime = convert_datetime(date, ENTRY_START_TIME)
        end_datetime = calculate_end_time(start_datetime, ENTRY_DURATION)

        entry_data = {
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "entry": response,
            }            
        entries.append(entry_data)

    # Write all entries to a single file
    all_entries_path = entry_dir /  'journal_entries.json'
    with open(all_entries_path, 'w') as file:
        json.dump(entries, file, indent=4)

def get_file_paths(directory):
    file_paths = [filepath for filepath in Path(directory).glob('*.txt')]
    file_paths = sorted(file_paths, key=extract_date)
    return file_paths

def make_journal_entries(profile='llm_v0'):

    # set up directories
    profile_dir = Path.cwd().parent /'data'/'sim' / 'profiles'/profile
    inputs_dir = profile_dir / "inputs"
    # Create a directory for the journal entries
    entry_dir = profile_dir / 'outputs' / 'final'
    entry_dir.mkdir(parents=True, exist_ok=True)

    # get sim params
    sim_params_path = inputs_dir / "sim_params.yaml"
    sim_params = load_yaml_file(sim_params_path)
    sim_dates = sim_params.get("dates")
    for k in sim_dates:
        sim_params['dates'][k] = convert_date(sim_dates[k])
    dates = get_days_from_range(sim_dates['start_date'], sim_dates['end_date'])


    # get bio
    bio = getattr(PROMPTS, profile)


    # get entry prompts
    entry_prompts_path = profile_dir / 'outputs' / 'intermediate' / 'entry_prompts.txt'
    full_text = load_text_from_file(entry_prompts_path)
    entry_prompts = full_text.split(ENTRY_PROMPT_DIVIDER)




    # Set up OpenAI API key
    openai.api_key = keys.OPENAI

    # Process each file
    process_files(bio, entry_prompts, dates, entry_dir)


